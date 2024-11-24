import json
import logging
import time
from typing import Any, Optional, override

from pysrc.adapters.kraken.asset_mappings import (
    asset_to_kraken,
    kraken_to_asset,
)
from pysrc.adapters.messages import SnapshotMessage, TradeMessage
from pysrc.util.exceptions import prod_assert
from pysrc.util.types import Asset, Market, OrderSide
from pysrc.util.websocket import WebSocketClient

_logger = logging.getLogger(__name__)


class KrakenFutureWebsocketClient(WebSocketClient):
    BASE_URL: str = "wss://futures.kraken.com/ws/v1"

    def __init__(
        self,
        subscribed_assets: list[Asset],
        retry_delay: int = 5,
        max_retries: Optional[int] = None,
    ) -> None:
        super().__init__(self.BASE_URL, retry_delay, max_retries)
        self.subscribed_assets: list[Asset] = subscribed_assets
        self.trade_messages: list[TradeMessage] = []
        # only to be updated immediately before passing to client
        self.snapshot_messages: dict[Asset, SnapshotMessage] = {
            asset: SnapshotMessage(
                -1,
                asset_to_kraken(asset, Market.KRAKEN_USD_FUTURE),
                [],
                [],
                Market.KRAKEN_USD_FUTURE,
            )
            for asset in subscribed_assets
        }
        self.subscription_confirmations: dict[str, bool] = {}
        self.bids: dict[Asset, dict[float, float]] = {
            asset: {} for asset in self.subscribed_assets
        }
        self.asks: dict[Asset, dict[float, float]] = {
            asset: {} for asset in self.subscribed_assets
        }

    @override
    async def on_connect(self) -> None:
        kraken_asset_ids = [
            asset_to_kraken(asset, Market.KRAKEN_USD_FUTURE)
            for asset in self.subscribed_assets
        ]
        subscription_messages = [
            {"event": "subscribe", "feed": "trade", "product_ids": kraken_asset_ids},
            {"event": "subscribe", "feed": "book", "product_ids": kraken_asset_ids},
        ]
        assert (
            self.ws is not None
        ), "WebSocket must be initialized before sending messages."
        for message in subscription_messages:
            await self.ws.send(json.dumps(message))
            _logger.warning(f"Sent subscription message: {message}")

    @override
    async def on_disconnect(self) -> None:
        _logger.warning("Disconnected from Kraken WebSocket.")

    @override
    async def on_message(self, message: dict[str, Any]) -> None:
        prod_assert(
            "event" in message, f"Received message with no event key: {message}"
        )
        prod_assert("feed" in message, f"Received message with no feed key: {message}")
        event = message["event"]
        feed_type = message["feed"]

        if event == "subscribed":
            product_ids = message.get("product_ids", [])
            self.subscription_confirmations[feed_type] = True
            _logger.warning(
                f"Subscribed to {feed_type} feed for products: {product_ids}"
            )
            return

        if feed_type == "trade_snapshot":
            prod_assert(
                self.subscription_confirmations["trade"] is True,
                "Cannot receieve trade_snapshot message without subscription to trades",
            )
            for trade_data in message.get("trades", []):
                trade_message = self._parse_trade_message(trade_data)
                self.trade_messages.append(trade_message)
            _logger.warning(
                f"Appended {len(message.get('trades', []))} trade messages."
            )

        elif feed_type == "trade":
            prod_assert(
                self.subscription_confirmations[feed_type] is True,
                "Cannot receieve trade message without subscription to trades",
            )
            trade_message = self._parse_trade_message(message)
            self.trade_messages.append(trade_message)

        elif feed_type == "book_snapshot":
            prod_assert(
                self.subscription_confirmations["book"] is True,
                "Cannot receieve book_snapshot message without subscription to book",
            )
            self._parse_book_snapshot(message)

        elif feed_type == "book":
            prod_assert(
                self.subscription_confirmations[feed_type] is True,
                "Cannot receieve book message without subscription to book",
            )
            prod_assert(
                "price" in message and "qty" in message,
                f"Received message without price/qty {message}",
            )
            feedcode = message["product_id"]
            price = float(message["price"])
            qty = float(message["qty"])
            asset = kraken_to_asset(feedcode)

            if message.get("side") == "buy":
                if qty != 0.0 and price in self.bids[asset]:
                    del self.bids[asset][price]
                else:
                    self.bids[asset][price] = qty

            if message.get("side") == "sell":
                if qty != 0.0 and price in self.asks[asset]:
                    del self.asks[asset][price]
                else:
                    self.asks[asset][price] = qty
        else:
            _logger.warning(f"Received unknown message feed type: {feed_type}")

    def _parse_trade_message(self, trade_data: dict[str, Any]) -> TradeMessage:
        prod_assert(
            "time" in trade_data
            and "product_id" in trade_data
            and "price" in trade_data
            and "qty" in trade_data,
            f"Missing TradeMessage param in message: {trade_data}",
        )
        return TradeMessage(
            time=trade_data["time"],
            feedcode=trade_data["product_id"],
            n_trades=1,
            price=float(trade_data["price"]),
            quantity=float(trade_data["qty"]),
            side=OrderSide.ASK if trade_data["side"] == "sell" else OrderSide.BID,
            market=Market.KRAKEN_USD_FUTURE,
        )

    def _parse_book_snapshot(self, data: dict[str, Any]) -> None:
        prod_assert(
            "product_id" in data,
            f"Received book message without feedcode in message: {data}",
        )
        feedcode = data["product_id"]
        asset = kraken_to_asset(feedcode)
        for bid in data.get("bids", []):
            price = float(bid["price"])
            qty = float(bid["qty"])
            self.bids[asset][price] = qty

        for ask in data.get("asks", []):
            price = float(ask["price"])
            qty = float(ask["qty"])
            self.asks[asset][price] = qty

    def poll_trades(self) -> list[TradeMessage]:
        trades = self.trade_messages[:]
        self.trade_messages.clear()
        return trades

    def poll_snapshots(self) -> dict[Asset, SnapshotMessage]:
        for asset in self.subscribed_assets:
            self.snapshot_messages[asset].time = int(time.time())
            self.snapshot_messages[asset].bids = []
            self.snapshot_messages[asset].asks = []

            for price, quantity in self.bids[asset].items():
                self.snapshot_messages[asset].bids.append((price, quantity))

            for price, quantity in self.asks[asset].items():
                self.snapshot_messages[asset].asks.append((price, quantity))

            self.snapshot_messages[asset].bids = sorted(
                self.snapshot_messages[asset].bids, key=lambda x: -x[0]
            )
            self.snapshot_messages[asset].asks = sorted(
                self.snapshot_messages[asset].asks
            )

        return self.snapshot_messages
