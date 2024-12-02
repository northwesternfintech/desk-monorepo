from collections import defaultdict, deque
from enum import Enum
from math import isclose
from threading import Condition
from typing import Optional

from pysrc.adapters.messages import SnapshotMessage
from pysrc.util.types import Market, OrderSide


class EventType(Enum):
    ORDER = 0
    EXECUTION = 1


class OrderEventType(Enum):
    PLACED = 0
    UPDATED = 1
    CANCELLED = 2
    REJECTED = 3
    EDIT_REJECTED = 4


class UpdateDelta:
    def __init__(self, side: OrderSide, timestamp: int, price: float, quantity: float):
        self.timestamp = timestamp
        self.side = side
        self.deltas = defaultdict(float)

        self.deltas[price] = quantity

    def add(self, price: float, quantity: float) -> None:
        self.deltas[price] += quantity

    def add_delta(self, other_delta: "UpdateDelta") -> None:
        for price, quantity in other_delta.deltas.items():
            self.deltas[price] += quantity


class OrderEventResponse:
    def __init__(
        self,
        deltas: list[UpdateDelta],
        continuation_token: Optional[str],
    ):
        self.deltas = deltas
        self.continuation_token = continuation_token


class MBPBook:
    def __init__(self, feedcode: str, market: Market):
        self._feedcode = feedcode
        self._market = market

        self._book: list[dict[float, float]] = [defaultdict(float), defaultdict(float)]

    def apply_delta(self, delta: UpdateDelta) -> None:
        book_side = self._book[delta.side.value - 1]

        for price, quantity in delta.deltas.items():
            book_side[price] += quantity

            if isclose(book_side[price], 0, rel_tol=1e-05, abs_tol=1e-08):
                del book_side[price]

    def to_snapshot_message(self, time: int) -> SnapshotMessage:
        bids = list(self._book[OrderSide.BID.value - 1].items())
        asks = list(self._book[OrderSide.ASK.value - 1].items())

        snapshot = SnapshotMessage(
            time=time, feedcode=self._feedcode, bids=[], asks=[], market=self._market
        )

        snapshot.bids = bids
        snapshot.asks = asks

        return snapshot

    def copy(self) -> "MBPBook":
        new_book = MBPBook(feedcode=self._feedcode, market=self._market)

        for i, side_orders in enumerate(self._book):
            for price, quantity in side_orders.items():
                new_book._book[i][price] = quantity

        return new_book


class ChunkedEventQueue:
    def __init__(self, num_chunks: int = 24):
        self._num_chunks = num_chunks

        if self._num_chunks <= 0:
            raise ValueError("num_chunks must be greater than zero")

        self._statuses = {
            EventType.ORDER: [False for _ in range(self._num_chunks)],
            EventType.EXECUTION: [False for _ in range(self._num_chunks)],
        }

        self._chunks: list[list[UpdateDelta]] = [[] for _ in range(self._num_chunks)]

        self._cond_var = Condition()

        self._queue: deque[UpdateDelta] = deque()

        self._cur_chunk = 0
        self._failed = False

    def empty(self) -> bool:
        return self._cur_chunk >= self._num_chunks and not self._queue

    def failed(self) -> bool:
        return self._failed

    def mark_done(self, event_type: EventType, chunk_idx: int) -> None:
        if self._statuses[event_type][chunk_idx]:
            raise ValueError(f"chunk_idx '{chunk_idx}' already completed")

        self._statuses[event_type][chunk_idx] = True

        with self._cond_var:
            self._cond_var.notify()

    def mark_failed(self) -> None:
        self._failed = True

        with self._cond_var:
            self._cond_var.notify()

    def put(
        self, deltas: list[UpdateDelta], event_type: EventType, chunk_idx: int
    ) -> None:
        if chunk_idx >= self._num_chunks:
            raise ValueError(f"chunk_idx '{chunk_idx}' out of bounds")

        if self._statuses[event_type][chunk_idx]:
            raise ValueError("Attempted to put item into a completed chunk")

        self._chunks[chunk_idx].extend(deltas)

        with self._cond_var:
            self._cond_var.notify()

    def _load_queue(self) -> bool:
        if self._queue:
            return True
        elif self.empty() or self.failed():
            return False

        with self._cond_var:
            self._cond_var.wait_for(
                lambda: all(
                    event_statuses[self._cur_chunk]
                    for event_statuses in self._statuses.values()
                )
                or self.failed()
            )

        if self.failed():
            return False

        chunk = self._chunks[self._cur_chunk]
        self._chunks[self._cur_chunk] = []
        chunk.sort(key=lambda x: x.timestamp)
        self._queue = deque(chunk)

        self._cur_chunk += 1

        if not self._queue:
            return self._load_queue()

        return True

    def peek(self) -> Optional[UpdateDelta]:
        res = self._load_queue()

        if not res:
            return None

        return self._queue[0]

    def get(self) -> Optional[UpdateDelta]:
        res = self._load_queue()

        if not res:
            return None

        return self._queue.popleft()
