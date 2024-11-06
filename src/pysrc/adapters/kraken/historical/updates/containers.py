from enum import Enum
from typing import Optional

from pysrc.adapters.kraken.future.utils import str_to_order_side
from pysrc.util.types import OrderSide


class OrderEventType(Enum):
    PLACED = 0
    UPDATED = 1
    CANCELLED = 2


class OrderEvent:
    def __init__(
        self,
        event_type: OrderEventType,
        uid: str,
        timestamp: int,
        side: OrderSide,
        quantity: float,
        price: float,
    ):
        self.event_type = event_type
        self.uid = uid
        self.timestamp = timestamp
        self.side = side
        self.quantity = quantity
        self.price = price


class OrderEventResponse:
    def __init__(
        self,
        events,
        continuation_token: Optional[str],
    ):
        self.events = events
        self.continuation_token = continuation_token
