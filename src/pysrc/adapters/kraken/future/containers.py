from enum import Enum
from typing import Optional

from pysrc.util.types import OrderSide

class OrderType(Enum):
    LMT = 0
    POST = 1
    IOC = 2
    MKT = 3
    STP = 4
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

class TriggerSignal(Enum):
    MARK = 0
    SPOT = 1
    LAST = 2

class Order:
    def __init__(
            self,
            order_type: OrderType,
            symbol: str,
            side: OrderSide,
            size: float,
            limit_price: Optional[float],
            stop_price: Optional[float],
            order_id: Optional[str],
            filled_size: Optional[float],
            unfilled_size: Optional[float],
            reduce_only: Optional[bool],
            trigger_signal: Optional[TriggerSignal],
            last_update_time: Optional[float]
    ):
        pass

class PriceUnit(Enum):
    QUOTE_CURRENCY = 0
    PERCENT = 1

class OrderRequest:
    def __init__(
            self,
            order: Order,
            process_before: str,
            trailing_stop_max_deviation: Optional[bool],
            trailing_stop_deviation_unit: Optional[PriceUnit],
            limit_price_offset_value: Optional[float],
            limit_price_offset_unit: Optional[PriceUnit]
    ):
        pass

class PositionSide(Enum):
    LONG = 0
    SHORT = 1

class OpenPosition:
    def __init__(
            self,
            position_side: PositionSide,
            symbol: str,
            price: float,
            fill_time: str,
            size: float
    ):
        pass

class TradeHistory:
    def __init__(
        self,
        price: float,
        side: Optional[OrderSide],
        size: float,
        time: str,
        trade_id: int,
        type: HistoryType,
        uid: str,
        instrument_identification_type: str,
        isin: str,
        price_notation: str,
        price_currency: str,
        notional_amount: float,
        notional_currency: str,
        publication_time: str,
        publication_venue: str,
        transaction_identification_code: str,
        to_be_cleared: bool
    )