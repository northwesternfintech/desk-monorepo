from enum import Enum


class LiquidityType(Enum):
    TAKER = 1
    MAKER = 2


class OrderSide(Enum):
    BID = 1
    ASK = 2


class Market(Enum):
    KRAKEN_SPOT = 1
    KRAKEN_USD_FUTURE = 2


class Asset(Enum):
    BTC = 1
    ETH = 2
    WIF = 3
    XRP = 4
    SOL = 5
    DOGE = 6
    TRX = 7
    ADA = 8
    AVAX = 9
    SHIB = 10
    DOT = 11
