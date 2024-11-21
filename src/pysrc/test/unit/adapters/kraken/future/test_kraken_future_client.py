from unittest.mock import MagicMock, patch

import pytest

from pysrc.adapters.kraken.future.containers import (
    Order,
    OrderRequest,
    OrderStatus,
    OrderType,
    PositionSide,
)
from pysrc.adapters.kraken.future.kraken_future_client import KrakenFutureClient
from pysrc.util.types import OrderSide


@pytest.fixture
def client() -> KrakenFutureClient:
    return KrakenFutureClient(private_key="", public_key="")


@patch.object(KrakenFutureClient, "_make_private_request")
def test_get_open_orders(
    mock_make_private_request: MagicMock, client: KrakenFutureClient
) -> None:
    mock_make_private_request.return_value = {
        "result": "success",
        "openOrders": [
            {
                "order_id": "59302619-41d2-4f0b-941f-7e7914760ad3",
                "symbol": "PI_XBTUSD",
                "side": "sell",
                "orderType": "lmt",
                "limitPrice": 10640,
                "unfilledSize": 304,
                "receivedTime": "2019-09-05T17:01:17.410Z",
                "status": "untouched",
                "filledSize": 0,
                "reduceOnly": True,
                "lastUpdateTime": "2019-09-05T17:01:17.410Z",
            },
            {
                "order_id": "022774bc-2c4a-4f26-9317-436c8d85746d",
                "symbol": "PI_XBTUSD",
                "side": "buy",
                "orderType": "lmt",
                "limitPrice": 7200,
                "unfilledSize": 1501,
                "receivedTime": "2019-09-05T16:41:35.173Z",
                "status": "untouched",
                "filledSize": 0,
                "reduceOnly": False,
                "lastUpdateTime": "2019-09-05T16:47:47.519Z",
            },
        ],
        "serverTime": "2019-09-05T17:08:18.138Z",
    }

    res = client.get_open_orders()
    assert len(res) == 2

    order_1 = res[0]
    assert order_1.order_id == "59302619-41d2-4f0b-941f-7e7914760ad3"
    assert order_1.symbol == "PI_XBTUSD"
    assert order_1.side == OrderSide.ASK
    assert order_1.order_type == OrderType.LMT
    assert order_1.limit_price == 10640
    assert order_1.unfilled_size == 304
    assert order_1.status == OrderStatus.UNTOUCHED
    assert order_1.filled_size == 0
    assert order_1.reduce_only
    assert order_1.last_update_time == "2019-09-05T17:01:17.410Z"
    assert order_1.size == 304

    order_2 = res[1]
    assert order_2.order_id == "022774bc-2c4a-4f26-9317-436c8d85746d"
    assert order_2.symbol == "PI_XBTUSD"
    assert order_2.side == OrderSide.BID
    assert order_2.order_type == OrderType.LMT
    assert order_2.limit_price == 7200
    assert order_2.unfilled_size == 1501
    assert order_2.status == OrderStatus.UNTOUCHED
    assert order_2.filled_size == 0
    assert not order_2.reduce_only
    assert order_2.last_update_time == "2019-09-05T16:47:47.519Z"
    assert order_2.size == 1501


@patch.object(KrakenFutureClient, "_make_private_request")
def test_get_open_positions(
    mock_make_private_request: MagicMock, client: KrakenFutureClient
) -> None:
    mock_make_private_request.return_value = {
        "result": "success",
        "openPositions": [
            {
                "side": "short",
                "symbol": "PI_XBTUSD",
                "price": 9392.749993345933,
                "fillTime": "2020-07-22T14:39:12.376Z",
                "size": 10000,
                "unrealizedFunding": 0.00001045432180096817,
            },
            {
                "side": "long",
                "symbol": "FI_XBTUSD_201225",
                "price": 9399.749966754434,
                "fillTime": "2020-07-22T14:39:12.376Z",
                "size": 20000,
            },
        ],
        "serverTime": "2020-07-22T14:39:12.376Z",
    }

    res = client.get_open_positions()
    assert len(res) == 2

    position_1 = res[0]
    assert position_1.position_side == PositionSide.SHORT
    assert position_1.symbol == "PI_XBTUSD"
    assert position_1.price == 9392.749993345933
    assert position_1.fill_time == "2020-07-22T14:39:12.376Z"
    assert position_1.size == 10000

    position_2 = res[1]
    assert position_2.position_side == PositionSide.LONG
    assert position_2.symbol == "FI_XBTUSD_201225"
    assert position_2.price == 9399.749966754434
    assert position_2.fill_time == "2020-07-22T14:39:12.376Z"
    assert position_2.size == 20000


@patch.object(KrakenFutureClient, "_make_private_request")
def test_send_order_placed(
    mock_make_private_request: MagicMock, client: KrakenFutureClient
) -> None:
    mock_make_private_request.return_value = {
        "result": "success",
        "sendStatus": {
            "order_id": "179f9af8-e45e-469d-b3e9-2fd4675cb7d0",
            "status": "placed",
            "receivedTime": "2019-09-05T16:33:50.734Z",
            "orderEvents": [
                {
                    "type": "PLACE",
                    "order": {
                        "orderId": "179f9af8-e45e-469d-b3e9-2fd4675cb7d0",
                        "type": "lmt",
                        "symbol": "PI_XBTUSD",
                        "side": "buy",
                        "quantity": 10000,
                        "filled": 0,
                        "limitPrice": 9400,
                        "reduceOnly": False,
                        "timestamp": "2019-09-05T16:33:50.734Z",
                        "lastUpdateTimestamp": "2019-09-05T16:33:50.734Z",
                    },
                }
            ],
        },
        "serverTime": "2019-09-05T16:33:50.734Z",
    }

    order = Order(
        symbol="PI_XBTUSD",
        side=OrderSide.BID,
        size=10000,
        order_type=OrderType.LMT,
        limit_price=9400,
    )

    order = client.send_order(OrderRequest(order=order))
    assert order.order_id == "179f9af8-e45e-469d-b3e9-2fd4675cb7d0"
    assert order.status == OrderStatus.PLACED


@patch.object(KrakenFutureClient, "_make_private_request")
def test_send_order_rejected(
    mock_make_private_request: MagicMock, client: KrakenFutureClient
) -> None:
    mock_make_private_request.return_value = {
        "result": "success",
        "sendStatus": {
            "order_id": "614a5298-0071-450f-83c6-0617ce8c6bc4",
            "status": "iocWouldNotExecute",
            "receivedTime": "2019-09-05T16:32:54.076Z",
            "orderEvents": [
                {
                    "type": "REJECT",
                    "uid": "614a5298-0071-450f-83c6-0617ce8c6bc4",
                    "reason": "IOC_WOULD_NOT_EXECUTE",
                    "order": {
                        "orderId": "614a5298-0071-450f-83c6-0617ce8c6bc4",
                        "type": "lmt",
                        "symbol": "PI_XBTUSD",
                        "side": "buy",
                        "quantity": 10000,
                        "filled": 0,
                        "limitPrice": 9400,
                        "reduceOnly": True,
                        "timestamp": "2019-09-05T16:32:54.076Z",
                        "lastUpdateTimestamp": "2019-09-05T16:32:54.076Z",
                    },
                }
            ],
        },
        "serverTime": "2019-09-05T16:32:54.077Z",
    }

    order = Order(
        symbol="PI_XBTUSD",
        side=OrderSide.BID,
        size=10000,
        order_type=OrderType.LMT,
        limit_price=9400,
    )

    order = client.send_order(OrderRequest(order=order))
    assert order.order_id == "614a5298-0071-450f-83c6-0617ce8c6bc4"
    assert order.status == OrderStatus.REJECTED


@patch.object(KrakenFutureClient, "_make_private_request")
def test_send_order_executed(
    mock_make_private_request: MagicMock, client: KrakenFutureClient
) -> None:
    mock_make_private_request.return_value = {
        "result": "success",
        "sendStatus": {
            "order_id": "61ca5732-3478-42fe-8362-abbfd9465294",
            "status": "placed",
            "receivedTime": "2019-12-11T17:17:33.888Z",
            "orderEvents": [
                {
                    "type": "EXECUTION",
                    "executionId": "e1ec9f63-2338-4c44-b40a-43486c6732d7",
                    "price": 7244.5,
                    "amount": 10,
                    "orderPriorExecution": {
                        "orderId": "61ca5732-3478-42fe-8362-abbfd9465294",
                        "type": "lmt",
                        "symbol": "PI_XBTUSD",
                        "side": "buy",
                        "quantity": 10,
                        "filled": 0,
                        "limitPrice": 7500,
                        "reduceOnly": False,
                        "timestamp": "2019-12-11T17:17:33.888Z",
                        "lastUpdateTimestamp": "2019-12-11T17:17:33.888Z",
                    },
                }
            ],
        },
        "serverTime": "2019-12-11T17:17:33.888Z",
    }

    order = Order(
        symbol="PI_XBTUSD",
        side=OrderSide.BID,
        size=10,
        order_type=OrderType.LMT,
        limit_price=7500,
    )

    order = client.send_order(OrderRequest(order=order))
    assert order.order_id == "61ca5732-3478-42fe-8362-abbfd9465294"
    assert order.status == OrderStatus.PLACED


@patch.object(KrakenFutureClient, "_make_private_request")
def test_cancel_order_success(
    mock_make_private_request: MagicMock, client: KrakenFutureClient
) -> None:
    mock_make_private_request.return_value = {
        "result": "success",
        "cancelStatus": {
            "status": "cancelled",
            "order_id": "cb4e34f6-4eb3-4d4b-9724-4c3035b99d47",
            "receivedTime": "2020-07-22T13:26:20.806Z",
            "orderEvents": [
                {
                    "type": "CANCEL",
                    "uid": "cb4e34f6-4eb3-4d4b-9724-4c3035b99d47",
                    "order": {
                        "orderId": "cb4e34f6-4eb3-4d4b-9724-4c3035b99d47",
                        "cliOrdId": "1234568",
                        "type": "lmt",
                        "symbol": "PI_XBTUSD",
                        "side": "buy",
                        "quantity": 5500,
                        "filled": 0,
                        "limitPrice": 8000,
                        "reduceOnly": False,
                        "timestamp": "2020-07-22T13:25:56.366Z",
                        "lastUpdateTimestamp": "2020-07-22T13:25:56.366Z",
                    },
                }
            ],
        },
        "serverTime": "2020-07-22T13:26:20.806Z",
    }
    status = client.cancel_order("cb4e34f6-4eb3-4d4b-9724-4c3035b99d47")
    assert status == OrderStatus.CANCELLED


@patch.object(KrakenFutureClient, "_make_private_request")
def test_cancel_order_filled(
    mock_make_private_request: MagicMock, client: KrakenFutureClient
) -> None:
    mock_make_private_request.return_value = {
        "result": "success",
        "cancelStatus": {
            "status": "filled",
            "order_id": "cb4e34f6-4eb3-4d4b-9724-4c3035b99d47",
            "receivedTime": "2020-07-22T13:26:20.806Z",
            "orderEvents": [
                {
                    "type": "CANCEL",
                    "uid": "cb4e34f6-4eb3-4d4b-9724-4c3035b99d47",
                    "order": {
                        "orderId": "cb4e34f6-4eb3-4d4b-9724-4c3035b99d47",
                        "cliOrdId": "1234568",
                        "type": "lmt",
                        "symbol": "PI_XBTUSD",
                        "side": "buy",
                        "quantity": 5500,
                        "filled": 0,
                        "limitPrice": 8000,
                        "reduceOnly": False,
                        "timestamp": "2020-07-22T13:25:56.366Z",
                        "lastUpdateTimestamp": "2020-07-22T13:25:56.366Z",
                    },
                }
            ],
        },
        "serverTime": "2020-07-22T13:26:20.806Z",
    }
    status = client.cancel_order("cb4e34f6-4eb3-4d4b-9724-4c3035b99d47")
    assert status == OrderStatus.FILLED


@patch.object(KrakenFutureClient, "_make_private_request")
def test_cancel_order_not_found(
    mock_make_private_request: MagicMock, client: KrakenFutureClient
) -> None:
    mock_make_private_request.return_value = {
        "result": "success",
        "cancelStatus": {
            "status": "notFound",
            "order_id": "cb4e34f6-4eb3-4d4b-9724-4c3035b99d47",
            "receivedTime": "2020-07-22T13:26:20.806Z",
            "orderEvents": [
                {
                    "type": "CANCEL",
                    "uid": "cb4e34f6-4eb3-4d4b-9724-4c3035b99d47",
                    "order": {
                        "orderId": "cb4e34f6-4eb3-4d4b-9724-4c3035b99d47",
                        "cliOrdId": "1234568",
                        "type": "lmt",
                        "symbol": "PI_XBTUSD",
                        "side": "buy",
                        "quantity": 5500,
                        "filled": 0,
                        "limitPrice": 8000,
                        "reduceOnly": False,
                        "timestamp": "2020-07-22T13:25:56.366Z",
                        "lastUpdateTimestamp": "2020-07-22T13:25:56.366Z",
                    },
                }
            ],
        },
        "serverTime": "2020-07-22T13:26:20.806Z",
    }
    status = client.cancel_order("cb4e34f6-4eb3-4d4b-9724-4c3035b99d47")
    assert status == OrderStatus.REJECTED
