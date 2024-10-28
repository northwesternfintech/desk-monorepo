from enum import Enum
from typing import Optional

from pysrc.util.types import OrderSide, PositionSide


class OrderType(Enum):
    LMT = 0
    POST = 1
    IOC = 2
    MKT = 3
    STOP = 4
    TAKE_PROFIT = 5
    TRAILING_STOP = 6


class OrderStatus(Enum):
    ENTERED_BOOK = 0
    FULLY_EXECUTED = 1
    REJECTED = 2
    CANCELLED = 3
    TRIGGER_PLACED = 4
    TRIGGER_ACTIVATION_FAILURE = 5
    UNTOUCHED = 6
    PARTIALLY_FILLED = 7
    PLACED = 8
    EDITED = 9
    FILLED = 10


class TriggerSignal(Enum):
    MARK = 0
    SPOT = 1
    LAST = 2


class Order:
    def __init__(
        self,
        symbol: str,
        side: OrderSide,
        size: Optional[float] = None,
        order_type: Optional[OrderType] = None,
        status: Optional[OrderStatus] = None,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        order_id: Optional[str] = None,
        filled_size: Optional[float] = None,
        unfilled_size: Optional[float] = None,
        reduce_only: Optional[bool] = None,
        trigger_signal: Optional[TriggerSignal] = None,
        last_update_time: Optional[float] = None,
    ):
        self.symbol = symbol
        self.side = side
        self.size = size
        self.order_type = order_type
        self.status = status
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.order_id = order_id
        self.filled_size = filled_size
        self.unfilled_size = unfilled_size
        self.reduce_only = reduce_only
        self.trigger_signal = trigger_signal
        self.last_update_time = last_update_time


class PriceUnit(Enum):
    QUOTE_CURRENCY = 0
    PERCENT = 1


class OrderRequest:
    def __init__(
        self,
        order: Order,
        process_before: Optional[str] = None,
        trailing_stop_max_deviation: Optional[bool] = None,
        trailing_stop_deviation_unit: Optional[PriceUnit] = None,
        limit_price_offset_value: Optional[float] = None,
        limit_price_offset_unit: Optional[PriceUnit] = None,
    ):
        self.order = order
        self.process_before = process_before
        self.trailing_stop_max_deviation = trailing_stop_max_deviation
        self.trailing_stop_deviation_unit = trailing_stop_deviation_unit
        self.limit_price_offset_value = limit_price_offset_value
        self.limit_price_offset_unit = limit_price_offset_unit


class OpenPosition:
    def __init__(
        self,
        position_side: PositionSide,
        symbol: str,
        price: float,
        fill_time: str,
        size: float,
    ):
        self.position_side = position_side
        self.symbol = symbol
        self.price = price
        self.fill_time = fill_time
        self.size = size
