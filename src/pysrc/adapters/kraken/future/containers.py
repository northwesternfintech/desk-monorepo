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

class TradeHistoryType(Enum):
    FILL = 1
    LIQUIDATION = 2
    ASSIGNMENT = 3
    TERMINATION = 4
    BLOCK = 5

class TakerSide(Enum):
    BUY = 1
    SELL = 2

class TradeHistory:
    def __init__(
        self,
        symbol: str,
        price: float,
        side: Optional[TakerSide],
        size: Optional[float],
        time: str,
        trade_id: int,
        historyType: Optional[TradeHistoryType],
        uid: Optional[TradeHistoryType],
        instrument_identification_type: Optional[str],
        isin: Optional[str],
        execution_venue: Optional[str],
        price_notation: Optional[str],
        price_currency: Optional[str],
        notional_amount: Optional[float],
        notional_currency: Optional[str],
        publication_time: Optional[str],
        publication_venue: Optional[str],
        transaction_identification_code: Optional[str],
        to_be_cleared: Optional[bool]
    ):
        self.symbol = symbol
        self.price = price
        self.side = side
        self.size = size
        self.time = time
        self.trade_id = trade_id
        self.type = historyType
        self.uid = uid
        self.instrument_identification_type = instrument_identification_type
        self.isin = isin
        self.execution_venue = execution_venue
        self.price_notation = price_notation
        self.price_currency = price_currency
        self.notional_amount = notional_amount
        self.notional_currency = notional_currency
        self.publication_time = publication_time
        self.publication_venue = publication_venue
        self.transaction_identification_code = transaction_identification_code
        self.to_be_cleared = to_be_cleared

class OrderbookEntry:
    def __init__(self, side: OrderSide, price: float, quantity: float):
        self.side = side
        self.price = price
        self.quantity = quantity

class Orderbook:
    def __init__(self, symbol: str, asks: list[OrderbookEntry], bids: list[OrderbookEntry]):
        self.symbol = symbol
        self.asks = asks
        self.bids = bids

