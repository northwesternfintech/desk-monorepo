from enum import Enum
from typing import Optional

from pysrc.adapters.messages import SnapshotMessage
from pysrc.util.types import Market, OrderSide
from collections import defaultdict


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
