from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from pysrc.adapters.kraken.asset_mappings import asset_to_kraken
from pysrc.adapters.messages import TradeMessage
from pysrc.data_handlers.kraken.historical.trades_data_handler import TradesDataHandler
from pysrc.data_loaders.base_data_loader import BaseDataLoader
from pysrc.util.types import Asset, Market


class TickTradesDataLoader(BaseDataLoader):
    def __init__(
        self,
        resource_path: Path,
        asset: Asset,
        market: Market,
        since: date,
        until: Optional[date] = None,
    ) -> None:
        try:
            feedcode = asset_to_kraken(asset, market)
        except Exception as _:
            raise ValueError(
                "Invalid asset or market - cannot convert to Kraken feedcode"
            )

        self._resource_path = resource_path
        self._asset_resource_path = resource_path / "trades" / feedcode
        if not self._asset_resource_path.exists():
            raise ValueError(
                f"Directory for asset trades data '{self._asset_resource_path}' doesn't exist"
            )

        self._asset = asset
        self._market = market
        self._handler = TradesDataHandler()

        self._since = since
        self._until = date.today() if not until else until
        if self._since >= self._until:
            raise ValueError(
                f"Dates since ({self._since.strftime("%m_%d_%Y")}) equal to or later than until ({self._until.strftime("%m_%d_%Y")})"
            )
        self._cur_date = since
        self._cur_path = self._asset_resource_path / self._cur_date.strftime(
            "%m_%d_%Y.bin"
        )
        if not self._cur_path.exists():
            raise ValueError(f"Expected file '{self._cur_path}' doesn't exist")
        self._cur_generator = self._handler.stream_read(self._cur_path)

        self._cur_epoch = self._date_to_epoch(self._cur_date)
        self._countdown = 86_400
        self._cur_trades: list[TradeMessage] = []
        self._next_trade: Optional[TradeMessage] = None

    def _date_to_epoch(self, d: date) -> int:
        dt = datetime.combine(d, datetime.min.time())
        return int(dt.replace(tzinfo=timezone.utc).timestamp())

    def get_data(self, since: date, until: date) -> list[TradeMessage]:
        if since >= until:
            raise ValueError(
                f"Dates since ({since.strftime("%m_%d_%Y")}) equal to or later than until ({until.strftime("%m_%d_%Y")})"
            )
        file_paths = []
        trades = []

        for i in range((until - since).days):
            cur = since + timedelta(days=i)
            cur_file_name = cur.strftime("%m_%d_%Y.bin")
            cur_path = self._asset_resource_path / cur_file_name
            if not cur_path.exists():
                raise ValueError(f"Expected file '{cur_path}' doesn't exist")
            file_paths.append(cur_path)

        for file_path in file_paths:
            trades.extend(self._handler.read(file_path))

        return trades

    def next(self) -> Optional[list[TradeMessage]]:
        if self._countdown == 0:
            if self._next_trade is not None:
                raise ValueError(
                    "Unexpected invariance breach: file contains trade from the next date"
                )
            self._cur_date += timedelta(days=1)
            self._cur_path = self._asset_resource_path / self._cur_date.strftime(
                "%m_%d_%Y.bin"
            )
            if not self._cur_path.exists():
                return None
            if self._cur_date >= self._until:
                return None
            if not self._cur_path.exists():
                return None
            self._cur_generator = self._handler.stream_read(self._cur_path)
            self._countdown = 86_400

        if self._next_trade is not None:
            if self._next_trade.time < self._cur_epoch:
                raise ValueError(
                    "Unexpected invariance breach: trade time should be monotonically increasing"
                )
            elif self._next_trade.time == self._cur_epoch:
                self._cur_trades = [self._next_trade]
                self._next_trade = None
            else:
                self._countdown -= 1
                self._cur_epoch += 1
                return []

        try:
            while True:
                new_trade = next(self._cur_generator)
                if new_trade.time < self._cur_epoch:
                    raise ValueError(
                        "Unexpected invariance breach: trade time should be monotonically increasing"
                    )
                elif new_trade.time == self._cur_epoch:
                    self._cur_trades.append(new_trade)
                else:
                    self._next_trade = new_trade
                    break
            self._countdown -= 1
            self._cur_epoch += 1
            res = self._cur_trades
            self._cur_trades = []
            return res

        except StopIteration:
            self._next_trade = None
            self._countdown -= 1
            self._cur_epoch += 1
            res = self._cur_trades
            self._cur_trades = []
            return res
