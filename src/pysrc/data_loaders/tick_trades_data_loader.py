from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from pysrc.adapters.messages import TradeMessage
from pysrc.data_loaders.base_data_loader import BaseDataLoader
from pysrc.data_loaders.raw_trades_data_loader import RawTradesDataLoader
from pysrc.util.types import Asset, Market


class TickTradesDataLoader(BaseDataLoader):
    def __init__(
        self,
        resource_path: Path,
        asset: Asset,
        market: Market,
        since: date,
        until: date,
    ) -> None:
        self._raw_loader = RawTradesDataLoader(
            resource_path=resource_path,
            asset=asset,
            market=market,
            since=since,
            until=until,
        )
        self._start_timestamp = self._date_to_timestamp(self._raw_loader._since)
        self._end_timestamp = self._date_to_timestamp(self._raw_loader._until)
        self._cur_timestamp = self._date_to_timestamp(self._raw_loader._since)
        self._cur_trades: list[TradeMessage] = []
        self._next_trade: Optional[TradeMessage] = None

    def _date_to_timestamp(self, d: date) -> int:
        dt = datetime.combine(d, datetime.min.time())
        return int(dt.replace(tzinfo=timezone.utc).timestamp())

    def get_data(self, since: date, until: date) -> list[list[TradeMessage]]:
        raw_data = self._raw_loader.get_data(since, until)
        res: list[list[TradeMessage]] = []
        start_timestamp = self._date_to_timestamp(since)
        end_timestamp = self._date_to_timestamp(until)
        idx = 0
        for timestamp in range(start_timestamp, end_timestamp):
            if idx == len(raw_data):
                res.append([])
                continue
            if raw_data[idx].time < timestamp:
                raise ValueError(
                    "Unexpected invariance breach: trade time should be monotonically increasing"
                )
            elif raw_data[idx].time > timestamp:
                res.append([])
            else:
                cur_trades = []
                while (idx < len(raw_data)) and (timestamp == raw_data[idx].time):
                    cur_trades.append(raw_data[idx])
                    idx += 1
                res.append(cur_trades)
        return res

    def next(self) -> Optional[list[TradeMessage]]:
        if self._cur_timestamp >= self._end_timestamp:
            return None

        if self._next_trade is not None:
            if self._next_trade.time < self._cur_timestamp:
                raise ValueError(
                    "Unexpected invariance breach: trade time should be monotonically increasing"
                )
            elif self._next_trade.time > self._cur_timestamp:
                self._cur_timestamp += 1
                return []
            else:
                self._cur_trades = [self._next_trade]
                self._next_trade = None

        while True:
            new_trade = self._raw_loader.next()
            if new_trade is None:
                break
            if new_trade.time < self._cur_timestamp:
                raise ValueError(
                    "Unexpected invariance breach: trade time should be monotonically increasing"
                )
            elif new_trade.time == self._cur_timestamp:
                self._cur_trades.append(new_trade)
            else:
                self._next_trade = new_trade
                break

        self._cur_timestamp += 1
        res = self._cur_trades
        self._cur_trades = []
        return res
