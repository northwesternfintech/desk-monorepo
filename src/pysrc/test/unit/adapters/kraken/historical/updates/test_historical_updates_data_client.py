from unittest.mock import MagicMock, patch
from pysrc.adapters.kraken.historical.updates.containers import UpdateDelta
from pysrc.adapters.kraken.historical.updates.historical_updates_data_client import (
    HistoricalUpdatesDataClient,
)

from pysrc.util.types import OrderSide
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
                            "limitPrice": "1234.56789",
                            "orderType": "string",
                            "quantity": "1234.56789",
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
                            "limitPrice": "1234.56789",
                            "orderType": "string",
                            "quantity": "1234.56789",
                            "reduceOnly": False,
                            "timestamp": 1604937694000,
                            "tradeable": "string",
                            "uid": "abc12345",
                        },
                        "oldOrder": {
                            "direction": "Buy",
                            "lastUpdateTimestamp": 1604937694000,
                            "limitPrice": "1234.56789",
                            "orderType": "string",
                            "quantity": "1234.56789",
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
                            "limitPrice": "1234.56789",
                            "orderType": "string",
                            "quantity": "1234.56789",
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
    assert res.deltas[0].price == 1234.56789
    assert res.deltas[0].quantity == 1234.56789
    assert res.deltas[0].sign == 1

    assert res.deltas[1].side == OrderSide.BID
    assert res.deltas[1].price == 1234.56789
    assert res.deltas[1].quantity == 1234.56789
    assert res.deltas[1].sign == 1

    assert res.deltas[2].side == OrderSide.BID
    assert res.deltas[2].price == 1234.56789
    assert res.deltas[2].quantity == 1234.56789
    assert res.deltas[2].sign == -1

    assert res.deltas[3].side == OrderSide.BID
    assert res.deltas[3].price == 1234.56789
    assert res.deltas[3].quantity == 1234.56789
    assert res.deltas[3].sign == -1
