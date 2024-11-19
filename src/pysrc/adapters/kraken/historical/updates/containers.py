from enum import Enum
import sys
from threading import Condition
from typing import Optional

from pysrc.adapters.messages import SnapshotMessage
from pysrc.util.types import Market, OrderSide
from collections import defaultdict, deque


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
    def __init__(
        self,
        side: OrderSide,
        timestamp: int,
        sign: float,
        quantity: float,
        price: float,
    ):
        self.timestamp = timestamp
        self.side = side
        self.sign = sign
        self.quantity = quantity
        self.price = price


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
        self._book[delta.side.value - 1][delta.price] += delta.sign * delta.quantity

        if self._book[delta.side.value - 1][delta.price] == 0:
            del self._book[delta.side.value - 1][delta.price]

    def to_snapshot_message(self, time: int) -> SnapshotMessage:
        bids = [
            [price, quantity]
            for price, quantity in self._book[OrderSide.BID.value - 1].items()
        ]

        asks = [
            [price, quantity]
            for price, quantity in self._book[OrderSide.ASK.value - 1].items()
        ]

        return SnapshotMessage(
            time=time,
            feedcode=self._feedcode,
            bids=bids,
            asks=asks,
            market=self._market,
        )
    
    def copy(self) -> 'MBPBook':
        new_book = MBPBook(
            feedcode=self._feedcode,
            market=self._market
        )

        for i, side_orders in enumerate(self._book):
            for price, quantity in side_orders.items():
                new_book._book[i][price] = quantity

        return new_book
    
class QueueStatus(Enum):
    IN_PROGRESS = 0
    DONE = 1

class ChunkedEventQueue:
    def __init__(self, num_chunks: int = 24):
        self._num_chunks = num_chunks

        if self._num_chunks <= 0:
            raise ValueError("num_chunks must be greater than zero")

        self._statuses = {
            EventType.ORDER: [QueueStatus.IN_PROGRESS for _ in range(self._num_chunks)],
            EventType.EXECUTION: [QueueStatus.IN_PROGRESS for _ in range(self._num_chunks)],
        }

        self._queues = {
            EventType.ORDER: [deque() for _ in range(self._num_chunks)],
            EventType.EXECUTION: [deque() for _ in range(self._num_chunks)],
        }

        self._cond_vars = {
            EventType.ORDER: [Condition() for _ in range(self._num_chunks)],
            EventType.EXECUTION: [Condition() for _ in range(self._num_chunks)],
        }

        self._cur_chunk = 0
        self._failed = False

    def empty(self) -> bool:
        return self._cur_chunk >= self._num_chunks
    
    def failed(self) -> bool:
        return self._failed
    
    def mark_done(self, event_type: EventType, chunk_idx: int) -> None:
        if self._statuses[event_type][chunk_idx] != QueueStatus.IN_PROGRESS:
            raise ValueError(f"chunk_idx '{chunk_idx}' already marked")
        
        d = self._queues[event_type][chunk_idx]
        self._queues[event_type][chunk_idx] = deque(sorted(d, key=lambda x: x.timestamp))
        
        self._statuses[event_type][chunk_idx] = QueueStatus.DONE
        cond_var = self._cond_vars[event_type][chunk_idx]
        with cond_var:
            cond_var.notify()

    def mark_failed(self) -> None:
        self._failed = True

        for event_cond_vars in self._cond_vars.values():
            for cond_var in event_cond_vars:
                with cond_var:
                    cond_var.notify()
    
    def put(self, deltas: list[UpdateDelta], event_type: EventType, chunk_idx: int) -> None:
        if chunk_idx >= self._num_chunks:
            raise ValueError(f"chunk_idx '{chunk_idx}' out of bounds")
        
        if self._statuses[event_type][chunk_idx] != QueueStatus.IN_PROGRESS:
            raise ValueError(f"Attempted to put item into a marked queue")
        
        self._queues[event_type][chunk_idx].extend(deltas)

        cond_var = self._cond_vars[event_type][chunk_idx]
        with cond_var:
            cond_var.notify()

    def _get_next_event_type(self) -> Optional[EventType]:
        if self.empty():
            return None
        
        order_cond_var = self._cond_vars[EventType.ORDER][self._cur_chunk]
        exec_cond_var = self._cond_vars[EventType.EXECUTION][self._cur_chunk]
        
        with order_cond_var:
            order_cond_var.wait_for(lambda: self._failed or self._statuses[EventType.ORDER][self._cur_chunk] != QueueStatus.IN_PROGRESS)

        with exec_cond_var:
            exec_cond_var.wait_for(lambda: self._failed or self._statuses[EventType.EXECUTION][self._cur_chunk] != QueueStatus.IN_PROGRESS)

        if self._failed:
            return None
        
        order_delta_queue = self._queues[EventType.ORDER][self._cur_chunk]
        exec_delta_queue = self._queues[EventType.EXECUTION][self._cur_chunk]
        
        order_event = UpdateDelta(OrderSide.ASK, sys.maxsize, 0.0, 0.0, 0.0)
        exec_event = UpdateDelta(OrderSide.ASK, sys.maxsize, 0.0, 0.0, 0.0)

        if order_delta_queue:
            order_event = order_delta_queue[0]

        if exec_delta_queue:
            exec_event = exec_delta_queue[0]

        if not order_delta_queue and not exec_delta_queue:
            self._cur_chunk += 1
            return self._get_next_event_type()

        if order_event.timestamp < exec_event.timestamp:
            return EventType.ORDER
        
        return EventType.EXECUTION


    def peek(self) -> UpdateDelta:
        next_event_type = self._get_next_event_type()

        if next_event_type is None:
            return None
        
        return self._queues[next_event_type][self._cur_chunk][0]
        
    
    def get(self) -> UpdateDelta:
        next_event_type = self._get_next_event_type()

        if next_event_type is None:
            return None
        
        order_delta_queue = self._queues[EventType.ORDER][self._cur_chunk]
        exec_delta_queue = self._queues[EventType.EXECUTION][self._cur_chunk]

        res = self._queues[next_event_type][self._cur_chunk].popleft()

        if not order_delta_queue and not exec_delta_queue:
            self._cur_chunk += 1
        
        return res