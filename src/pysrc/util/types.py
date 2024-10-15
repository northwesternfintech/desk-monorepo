from enum import Enum


class LiquidityType(Enum):
    TAKER = 0
    MAKER = 1


class OrderSide(Enum):
    BID = 0
    ASK = 1


class Market(Enum):
    KRAKEN_SPOT = 0
    KRAKEN_USD_FUTURE = 1


class Asset(Enum):
    BTC = 0
    ETH = 1
    WIF = 2
    XRP = 3
    SOL = 4
    DOGE = 5
    TRX = 6
    ADA = 7
    AVAX = 8
    SHIB = 9
    DOT = 10
