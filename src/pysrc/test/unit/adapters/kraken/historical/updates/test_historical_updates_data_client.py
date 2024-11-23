import os
import random
import shutil
import threading
import time
import typing
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from pyzstd import CParameter, compress

from pysrc.adapters.kraken.historical.updates.containers import (
    ChunkedEventQueue,
    EventType,
    MBPBook,
    UpdateDelta,
)
from pysrc.adapters.kraken.historical.updates.historical_updates_data_client import (
    HistoricalUpdatesDataClient,
)
from pysrc.adapters.messages import SnapshotMessage
from pysrc.test.helpers import get_resources_path
from pysrc.util.types import Asset, Market, OrderSide

resource_path = str(get_resources_path(__file__))


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

    book_copy = book.copy()

    assert book_copy != book
    assert book_copy._feedcode == book._feedcode
    assert book_copy._market == book._market
    assert book_copy._book == book._book

    book_copy._book[0][-1] = -1

    assert book_copy._book != book._book


def random_fill_queue(queue: ChunkedEventQueue) -> None:
    assert queue._num_chunks == 5

    r = list(range(5))
    random.shuffle(r)
    for i in r:
        choice = random.randint(0, 1)
        event_type = EventType(choice % 2)
        other_event_type = EventType(1 - (choice % 2))

        for j in range(3):
            delta = UpdateDelta(OrderSide.BID, i * 4 + j, 1, i * 4 + j, i * 4 + j)
            queue.put([delta], event_type, i)

        time.sleep(0.05)
        queue.mark_done(event_type, i)
        time.sleep(0.05)

        delta = UpdateDelta(OrderSide.BID, i * 4 + 3, 1, i * 4 + 3, i * 4 + 3)
        queue.put([delta], other_event_type, i)

        time.sleep(0.05)
        queue.mark_done(other_event_type, i)
        time.sleep(0.05)


def test_chunked_event_queue() -> None:
    queue = ChunkedEventQueue(num_chunks=5)

    thread = threading.Thread(target=random_fill_queue, args=(queue,))

    thread.start()

    for i in range(20):
        assert not queue.empty()

        delta = queue.peek()
        assert delta is not None
        assert delta.side == OrderSide.BID
        assert delta.timestamp == i
        assert delta.sign == 1
        assert delta.price == i
        assert delta.quantity == i

        delta = queue.get()
        assert delta is not None
        assert delta.side == OrderSide.BID
        assert delta.timestamp == i
        assert delta.sign == 1
        assert delta.price == i
        assert delta.quantity == i

    assert queue.empty()
    assert queue.peek() is None
    assert queue.get() is None

    thread.join()

    queue = ChunkedEventQueue(num_chunks=5)
    assert not queue.failed()
    queue.mark_failed()
    assert queue.failed()

    assert queue.peek() is None


@pytest.fixture
def client() -> HistoricalUpdatesDataClient:
    return HistoricalUpdatesDataClient(resource_path)


ORDER_EVENTS: dict[str, typing.Any] = {
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
            "timestamp": 1000,
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
            "timestamp": 2000,
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
            "timestamp": 10000,
            "uid": "abc123456",
        },
    ],
    "len": 0,
}

EXECUTION_EVENTS: dict[str, typing.Any] = {
    "elements": [
        {
            "uid": "a244c3b2-0543-41e5-81bb-f000050eb537",
            "timestamp": 2000,
            "event": {
                "Execution": {
                    "execution": {
                        "uid": "1f466249-5736-43d0-bff4-096c9229ecb0",
                        "makerOrder": {
                            "uid": "97c27b3a-6a41-41a4-9d0e-e5399e7947e7",
                            "tradeable": "PF_XBTUSD",
                            "direction": "Buy",
                            "quantity": "3000",
                            "timestamp": 1730786549972,
                            "limitPrice": "68717.5",
                            "orderType": "Limit",
                            "reduceOnly": False,
                            "lastUpdateTimestamp": 1730786549972,
                        },
                        "takerOrder": {
                            "uid": "bfce0e50-fc61-443e-977e-e8ce419bac6e",
                            "tradeable": "PF_XBTUSD",
                            "direction": "Sell",
                            "quantity": "3000",
                            "timestamp": 1730786567508,
                            "limitPrice": "68717.5",
                            "orderType": "IoC",
                            "reduceOnly": False,
                            "lastUpdateTimestamp": 1730786567508,
                        },
                        "timestamp": 2000,
                        "quantity": "3000",
                        "price": "68717.5",
                        "markPrice": "68725.34039593864",
                        "limitFilled": True,
                        "usdValue": "3000.00",
                    },
                    "takerReducedQuantity": "",
                }
            },
        }
    ]
}


@patch.object(HistoricalUpdatesDataClient, "_request")
def test_get_order_events(
    mock_make_request: MagicMock, client: HistoricalUpdatesDataClient
) -> None:
    mock_make_request.return_value = ORDER_EVENTS

    res = client._get_order_events("")
    assert res.continuation_token == "c3RyaW5n"
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


@patch.object(HistoricalUpdatesDataClient, "_request")
def test_get_execution_events(
    mock_make_request: MagicMock, client: HistoricalUpdatesDataClient
) -> None:
    mock_make_request.return_value = EXECUTION_EVENTS

    res = client._get_execution_events("")
    assert res.continuation_token is None
    assert len(res.deltas) == 2

    assert res.deltas[0].side == OrderSide.BID
    assert res.deltas[0].price == 68717.5
    assert res.deltas[0].quantity == 3000
    assert res.deltas[0].sign == -1

    assert res.deltas[1].side == OrderSide.ASK
    assert res.deltas[1].price == 68717.5
    assert res.deltas[1].quantity == 3000
    assert res.deltas[1].sign == -1


@patch.object(HistoricalUpdatesDataClient, "_request")
def test_queue_events_for_day(
    mock_make_request: MagicMock, client: HistoricalUpdatesDataClient
) -> None:
    client._queue._cond_var = MagicMock()
    order_return_val = ORDER_EVENTS.copy()
    order_return_val["continuationToken"] = None
    mock_make_request.return_value = order_return_val

    client._queue_events_for_chunk(
        "",
        datetime(year=2024, month=11, day=5),
        datetime(year=2024, month=11, day=5),
        0,
        EventType.ORDER,
    )

    assert client._queue._statuses[EventType.ORDER][0]
    assert len(client._queue._chunks[0]) == 4
    client._queue._cond_var.notify.assert_called()

    client._queue._cond_var = MagicMock()
    mock_make_request.return_value = EXECUTION_EVENTS
    client._queue_events_for_chunk(
        "",
        datetime(year=2024, month=11, day=5),
        datetime(year=2024, month=11, day=5),
        0,
        EventType.EXECUTION,
    )
    assert client._queue._statuses[EventType.EXECUTION][0]
    assert len(client._queue._chunks[0]) == 6
    client._queue._cond_var.notify.assert_called()

    client._queue.peek()
    assert len(client._queue._queue) == 6
    assert not (client._queue.empty() or client._queue.failed())
    assert client._queue._cur_chunk == 1


def test_compute_next_snapshot(client: HistoricalUpdatesDataClient) -> None:
    client._cur_mbp_book = MBPBook(feedcode="PF_XBTUSD", market=Market.KRAKEN_USD_FUTURE)
    client._queue = ChunkedEventQueue(num_chunks=1)
    client._cur_sec = 1

    for e in ORDER_EVENTS["elements"]:
        client._queue.put(client._delta_from_order_event(e), EventType.ORDER, 0)

    for e in EXECUTION_EVENTS["elements"]:
        client._queue.put(client._delta_from_execution_event(e), EventType.EXECUTION, 0)

    client._queue.mark_done(EventType.ORDER, 0)
    client._queue.mark_done(EventType.EXECUTION, 0)

    snapshot = client._compute_next_snapshot()
    assert snapshot
    assert snapshot.time == 1
    assert snapshot.feedcode == "PF_XBTUSD"
    assert snapshot.market == Market.KRAKEN_USD_FUTURE
    assert len(snapshot.bids) == 0
    assert len(snapshot.asks) == 1
    assert (1, 2) in snapshot.asks
    assert client._cur_sec == 2

    snapshot = client._compute_next_snapshot()
    assert snapshot
    assert snapshot.time == 2
    assert snapshot.feedcode == "PF_XBTUSD"
    assert snapshot.market == Market.KRAKEN_USD_FUTURE
    assert len(snapshot.bids) == 3
    assert len(snapshot.asks) == 2
    assert (1, 2) in snapshot.asks
    assert (68717.5, -3000) in snapshot.asks
    assert (3, 4) in snapshot.bids
    assert (5, -6) in snapshot.bids
    assert (68717.5, -3000) in snapshot.bids
    assert client._cur_sec == 10

    snapshot = client._compute_next_snapshot()
    assert snapshot
    assert snapshot.time == 10
    assert snapshot.feedcode == "PF_XBTUSD"
    assert snapshot.market == Market.KRAKEN_USD_FUTURE
    assert len(snapshot.bids) == 4
    assert len(snapshot.asks) == 2
    assert (1, 2) in snapshot.asks
    assert (68717.5, -3000) in snapshot.asks
    assert (3, 4) in snapshot.bids
    assert (5, -6) in snapshot.bids
    assert (68717.5, -3000) in snapshot.bids
    assert (7, -8) in snapshot.bids

    assert len(client._queue._queue) == 0

    snapshot = client._compute_next_snapshot()
    assert snapshot is None


@patch.object(HistoricalUpdatesDataClient, "_request")
def test_fail_download_updates(
    mock_make_request: MagicMock, client: HistoricalUpdatesDataClient
) -> None:
    mock_make_request.side_effect = ValueError()

    with pytest.raises(ValueError) as e_info:
        client.download_updates(
            asset=Asset.BTC, since=datetime(year=2024, month=11, day=5)
        )

    assert (
        e_info.value.args[0]
        == "Failed to download updates for 'PF_XBTUSD' for date '11_05_2024'"
    )

    shutil.rmtree(resource_path)
