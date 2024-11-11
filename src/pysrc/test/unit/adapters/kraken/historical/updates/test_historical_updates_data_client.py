from unittest.mock import MagicMock, patch
from pysrc.adapters.kraken.historical.updates.containers import MBPBook, UpdateDelta
from pysrc.adapters.kraken.historical.updates.historical_updates_data_client import (
    HistoricalUpdatesDataClient,
)

from pysrc.util.types import Market, OrderSide
import pytest


@pytest.fixture
def client() -> HistoricalUpdatesDataClient:
    return HistoricalUpdatesDataClient("")


@patch.object(HistoricalUpdatesDataClient, "_request")
def test_get_order_events(
    mock_make_request: MagicMock, client: HistoricalUpdatesDataClient
):
    mock_make_request.return_value = {
        "continuationToken": "c3RyaW5n",
        "elements": [
            {
                "event": {
                    "OrderPlaced": {
                        "order": {
                            "direction": "Sell",
                            "lastUpdateTimestamp": 1604937694000,
                            "limitPrice": "1",
                            "orderType": "string",
                            "quantity": "2",
                            "reduceOnly": False,
                            "timestamp": 1604937694000,
                            "tradeable": "string",
                            "uid": "abc1234",
                        },
                        "reason": "string",
                        "reducedQuantity": "string",
                    }
                },
                "timestamp": 1604937694000,
                "uid": "abc1234",
            },
            {
                "event": {
                    "OrderUpdated": {
                        "newOrder": {
                            "direction": "Buy",
                            "lastUpdateTimestamp": 1604937694000,
                            "limitPrice": "3",
                            "orderType": "string",
                            "quantity": "4",
                            "reduceOnly": False,
                            "timestamp": 1604937694000,
                            "tradeable": "string",
                            "uid": "abc12345",
                        },
                        "oldOrder": {
                            "direction": "Buy",
                            "lastUpdateTimestamp": 1604937694000,
                            "limitPrice": "5",
                            "orderType": "string",
                            "quantity": "6",
                            "reduceOnly": False,
                            "timestamp": 1604937694000,
                            "tradeable": "string",
                            "uid": "abc12345",
                        },
                        "reason": "string",
                        "reducedQuantity": "1234.56789",
                    }
                },
                "timestamp": 1604937694001,
                "uid": "abc12345",
            },
            {
                "event": {
                    "OrderCancelled": {
                        "order": {
                            "direction": "Buy",
                            "lastUpdateTimestamp": 1604937694000,
                            "limitPrice": "7",
                            "orderType": "string",
                            "quantity": "8",
                            "reduceOnly": False,
                            "timestamp": 1604937694000,
                            "tradeable": "string",
                            "uid": "abc123456",
                        },
                        "reason": "string",
                    }
                },
                "timestamp": 1604937694002,
                "uid": "abc123456",
            },
        ],
        "len": 0,
    }

    res = client._get_order_events("")
    assert len(res.deltas) == 4

    assert res.deltas[0].side == OrderSide.ASK
    assert res.deltas[0].price == 1
    assert res.deltas[0].quantity == 2
    assert res.deltas[0].sign == 1

    assert res.deltas[1].side == OrderSide.BID
    assert res.deltas[1].price == 3
    assert res.deltas[1].quantity == 4
    assert res.deltas[1].sign == 1

    assert res.deltas[2].side == OrderSide.BID
    assert res.deltas[2].price == 5
    assert res.deltas[2].quantity == 6
    assert res.deltas[2].sign == -1

    assert res.deltas[3].side == OrderSide.BID
    assert res.deltas[3].price == 7
    assert res.deltas[3].quantity == 8
    assert res.deltas[3].sign == -1


def test_mbp_book() -> None:
    book = MBPBook("BONKUSD", Market.KRAKEN_USD_FUTURE)

    book.apply_delta(UpdateDelta(OrderSide.BID, 0, 1, 10, 12))
    assert book._book[OrderSide.BID.value - 1][12] == 10
    assert not book._book[OrderSide.ASK.value - 1]

    book.apply_delta(UpdateDelta(OrderSide.ASK, 0, 1, 10, 15))
    assert book._book[OrderSide.ASK.value - 1][15] == 10

    book.apply_delta(UpdateDelta(OrderSide.BID, 0, -1, 3, 12))
    assert book._book[OrderSide.BID.value - 1][12] == 7

    book.apply_delta(UpdateDelta(OrderSide.BID, 0, -1, 7, 12))
    assert 12 not in book._book[OrderSide.BID.value - 1]

    book.apply_delta(UpdateDelta(OrderSide.BID, 0, 1, 10, 12))

    snapshot = book.to_snapshot_message(0)
    assert snapshot.time == 0
    assert snapshot.feedcode == "BONKUSD"
    assert snapshot.market == Market.KRAKEN_USD_FUTURE

    assert snapshot.asks == [(15, 10)]
    assert snapshot.bids == [(12, 10)]