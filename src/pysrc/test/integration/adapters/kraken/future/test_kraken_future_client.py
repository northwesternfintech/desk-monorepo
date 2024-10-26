# test account
# 4r4ssd86@futures-demo.com
# test password
# 7aszuj6oi3dduwvbhp6m
# public
# mxNWPOkWM9kcAJMNqvgkhtzLJmBqXOqI59GdxrIJ1bx5Zzc/qJfRY/Re
# private
# iw8uwgGZGfP1x9YnSB6Q8sQbuYKwlrNITqoLoe9ue292ReukNuQ02UQ3Eb93Wu629TEZIIZehEnkWMVFmYB3Y34B

import os
from pysrc.adapters.kraken.future.containers import Order, OrderRequest, OrderStatus, OrderType, TradeHistoryType, TradeHistory
from pysrc.adapters.kraken.future.kraken_future_client import KrakenFutureClient
from pysrc.util.types import OrderSide

import pytest

@pytest.fixture
def client() -> KrakenFutureClient:
    public_key = os.getenv("KRAKEN_FUTURE_API_PUBLIC_KEY")
    private_key = os.getenv("KRAKEN_FUTURE_API_PRIVATE_KEY")

    print(public_key, private_key)
    print(os.environ)

    assert public_key and private_key, "Missing Kraken future API keys"

    return KrakenFutureClient(
        public_key=public_key,
        private_key=private_key,
        use_live_api=False)

def test_place_and_cancel(client: KrakenFutureClient) -> None:
    # cancel any existing orders
    open_orders = client.get_open_orders()
    for order in open_orders:
        client.cancel_order(order.order_id)

    open_orders = client.get_open_orders()
    assert len(open_orders) == 0

    orders_to_place = [
        Order(
            symbol="PI_XBTUSD",
            side=OrderSide.BID,
            size=1,
            order_type=OrderType.LMT,
            limit_price=1.00
        ),
        Order(
            symbol="PI_XBTUSD",
            side=OrderSide.BID,
            size=1,
            order_type=OrderType.LMT,
            limit_price=2.00
        ),
        Order(
            symbol="PI_XBTUSD",
            side=OrderSide.ASK,
            size=1,
            order_type=OrderType.LMT,
            limit_price=100000
        )
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

def test_get_history(client: KrakenFutureClient) -> None:
    results = client.get_history("PI_XBTUSD")
    assert len(results) > 0

def test_get_orderbook(client: KrakenFutureClient) -> None:
    results = client.get_orderbook("PI_XBTUSD")
    assert len(results.asks) > 0
    assert len(results.bids) > 0