from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from pysrc.adapters.kraken.asset_mappings import kraken_to_asset
from pysrc.adapters.kraken.future.kraken_future_websocket_client import (
    KrakenFutureWebsocketClient,
)
from pysrc.adapters.messages import SnapshotMessage, TradeMessage
from pysrc.util.types import Asset, Market, OrderSide


@pytest.fixture
def client() -> KrakenFutureWebsocketClient:
    return KrakenFutureWebsocketClient(subscribed_assets=[Asset.BTC, Asset.ETH])


def test_parse_trade_message(client: KrakenFutureWebsocketClient) -> None:
    trade_data: dict[str, Any] = {
        "time": 1612269657781,
        "product_id": "PF_XBTUSD",
        "qty": "440",
        "price": "34893",
        "side": "sell",
    }

    expected_message: TradeMessage = TradeMessage(
        time=1612269657781,
        feedcode="PF_XBTUSD",
        n_trades=1,
        price=34893.0,
        quantity=440.0,
        side=OrderSide.ASK,
        market=Market.KRAKEN_USD_FUTURE,
    )

    trade_message: TradeMessage = client._parse_trade_message(trade_data)
    assert trade_message == expected_message


def test_parse_book_snapshot(client: KrakenFutureWebsocketClient) -> None:
    snapshot_data: dict[str, int | str | list] = {
        "timestamp": 1612269825817,
        "product_id": "PF_XBTUSD",
        "bids": [
            {"price": "34892.5", "qty": "6385"},
            {"price": "34892", "qty": "10924"},
        ],
        "asks": [
            {"price": "34911.5", "qty": "20598"},
            {"price": "34912", "qty": "2300"},
        ],
    }

    expected_message: SnapshotMessage = SnapshotMessage(
        time=1612269825817,
        feedcode="PF_XBTUSD",
        bids=[[34892.5, 6385.0], [34892.0, 10924.0]],
        asks=[[34911.5, 20598.0], [34912.0, 2300.0]],
        market=Market.KRAKEN_USD_FUTURE,
    )

    client._parse_book_snapshot(snapshot_data)
    snapshot_message = client.poll_snapshots()[Asset.BTC]
    assert snapshot_message.bids == expected_message.bids
    assert snapshot_message.asks == expected_message.asks
    assert snapshot_message.feedcode == expected_message.feedcode
