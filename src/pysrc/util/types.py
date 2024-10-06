from enum import Enum


class LiquidityType(Enum):
    TAKER = 0
    MAKER = 1


class OrderSide(Enum):
    BID = 0
    ASK = 1
