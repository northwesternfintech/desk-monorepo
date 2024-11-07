from enum import Enum
from typing import Optional

from pysrc.adapters.kraken.future.utils import str_to_order_side
from pysrc.util.types import OrderSide
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
        sign: float,
        quantity: float,
        price: float,
    ):
        self.side = side
        self.sign = sign
        self.quantity = quantity
        self.price = price

class OrderEventResponse:
    def __init__(
        self,
        deltas,
        continuation_token: Optional[str],
    ):
        self.deltas = deltas
        self.continuation_token = continuation_token

class MBPBook:
    def __init__(
        self
    ):
        self._book = [
            defaultdict(float),
            defaultdict(float)
        ]

    def apply_deltas(
        self,
        deltas: list[UpdateDelta]
    ):
        for d in deltas:
            self._book[d.side.value][d.price] += d.sign * d.quantity
