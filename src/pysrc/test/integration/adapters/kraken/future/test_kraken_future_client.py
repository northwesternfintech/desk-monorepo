import os
from pysrc.adapters.kraken.future.containers import (
    Order,
    OrderRequest,
    OrderStatus,
    OrderType,
)
from pysrc.adapters.kraken.future.kraken_future_client import KrakenFutureClient
from pysrc.util.types import OrderSide

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("KRAKEN_FUTURE_API_PUBLIC_KEY") is None
    or os.getenv("KRAKEN_FUTURE_API_PRIVATE_KEY") is None,
    reason="Missing Kraken future API keys",
)


@pytest.fixture
def client() -> KrakenFutureClient:
    public_key = os.getenv("KRAKEN_FUTURE_API_PUBLIC_KEY")
    private_key = os.getenv("KRAKEN_FUTURE_API_PRIVATE_KEY")

    assert public_key and private_key, "Missing Kraken future API keys"

    client = KrakenFutureClient(
        public_key=public_key, private_key=private_key, use_live_api=False
    )

    return client


def test_place_and_cancel(client) -> None:
    # cancel any existing orders
    open_orders = client.get_open_orders()
    for order in open_orders:
        client.cancel_order(order.order_id)

    orders_to_place = [
        Order(
            symbol="PI_XBTUSD",
            side=OrderSide.BID,
            size=1,
            order_type=OrderType.LMT,
            limit_price=1.00,
        ),
        Order(
            symbol="PI_XBTUSD",
            side=OrderSide.BID,
            size=1,
            order_type=OrderType.LMT,
            limit_price=2.00,
        ),
        Order(
            symbol="PI_XBTUSD",
            side=OrderSide.ASK,
            size=1,
            order_type=OrderType.LMT,
            limit_price=100000,
        ),
    ]

    # check that orders placed
    placed_orders = []
    for order in orders_to_place:
        res = client.send_order(OrderRequest(order=order))
        assert res.status == OrderStatus.PLACED

        placed_orders.append(res)

    # check that orders show up in open orders
    open_orders = client.get_open_orders()
    assert len(open_orders) == 3

    open_order_ids = [order.order_id for order in open_orders]
    placed_order_ids = [order.order_id for order in placed_orders]

    assert set(open_order_ids) == set(placed_order_ids)

    # cancel one order
    order_to_cancel = placed_orders[0]
    res = client.cancel_order(order_to_cancel.order_id)
    assert res == OrderStatus.CANCELLED

    # check that order is no longer in open orders
    open_orders = client.get_open_orders()
    open_order_ids = [order.order_id for order in open_orders]
    assert order_to_cancel.order_id not in open_order_ids

    # cancel all orders
    res = client.cancel_all_orders("PI_XBTUSD")
    assert set(res) == set(open_order_ids)


def test_edit_order(client) -> None:
    # cancel any existing orders
    open_orders = client.get_open_orders()
    for order in open_orders:
        client.cancel_order(order.order_id)

    order = Order(
        symbol="PI_XBTUSD",
        side=OrderSide.BID,
        size=1,
        order_type=OrderType.LMT,
        limit_price=1.00,
    )

    res = client.send_order(OrderRequest(order=order))
    assert res.status == OrderStatus.PLACED

    new_order = Order(
        order_id=order.order_id,
        symbol="PI_XBTUSD",
        side=OrderSide.BID,
        size=1,
        order_type=OrderType.LMT,
        limit_price=2.00,
    )

    client.edit_order(OrderRequest(order=new_order))

    placed_order = client.get_open_orders()[0]
    assert placed_order.order_id == order.order_id
    assert placed_order.limit_price == new_order.limit_price

    assert client.cancel_order(order.order_id) == OrderStatus.CANCELLED


def test_batch_place_and_cancel(client) -> None:
    # cancel any existing orders
    open_orders = client.get_open_orders()
    open_order_ids = [order.order_id for order in open_orders]
    cancel_statuses = client.batch_cancel_order(open_order_ids)

    for order_id in open_order_ids:
        assert cancel_statuses[order_id] == OrderStatus.CANCELLED

    # place orders
    orders_to_place = [
        Order(
            symbol="PI_XBTUSD",
            side=OrderSide.BID,
            size=1,
            order_type=OrderType.LMT,
            limit_price=1.00,
        ),
        Order(
            symbol="PI_XBTUSD",
            side=OrderSide.BID,
            size=1,
            order_type=OrderType.LMT,
            limit_price=2.00,
        ),
        Order(
            symbol="PI_XBTUSD",
            side=OrderSide.ASK,
            size=1,
            order_type=OrderType.LMT,
            limit_price=100000,
        ),
    ]
    order_requests = [OrderRequest(order=order) for order in orders_to_place]

    client.batch_send_order(order_requests)
    for order in orders_to_place:
        assert order.status == OrderStatus.PLACED

    order_ids = [order.order_id for order in orders_to_place]
    cancel_statuses = client.batch_cancel_order(order_ids)

    open_orders = client.get_open_orders()
    assert len(open_orders) == 0


def test_batch_edit_order(client) -> None:
    # cancel any existing orders
    open_orders = client.get_open_orders()
    open_order_ids = [order.order_id for order in open_orders]
    client.batch_cancel_order(open_order_ids)

    # place orders
    orders_to_place = [
        Order(
            symbol="PI_XBTUSD",
            side=OrderSide.BID,
            size=1,
            order_type=OrderType.LMT,
            limit_price=1.00,
        ),
        Order(
            symbol="PI_XBTUSD",
            side=OrderSide.BID,
            size=1,
            order_type=OrderType.LMT,
            limit_price=2.00,
        ),
    ]
    order_requests = [OrderRequest(order=order) for order in orders_to_place]

    client.batch_send_order(order_requests)
    for order in orders_to_place:
        assert order.status == OrderStatus.PLACED

    # edit orders
    for order in orders_to_place:
        order.limit_price *= 3

    new_order_requests = [OrderRequest(order=order) for order in orders_to_place]
    res = client.batch_edit_order(new_order_requests)

    for order_request in new_order_requests:
        assert res[order_request]
        assert order_request.order.status == OrderStatus.PLACED

    # check that orders were actually edited
    placed_orders = client.get_open_orders()
    for order in placed_orders:
        matching_order = [o for o in orders_to_place if o.order_id == order.order_id][0]
        assert order.limit_price == matching_order.limit_price

    # cancel orders
    client.batch_cancel_order([order.order_id for order in placed_orders])