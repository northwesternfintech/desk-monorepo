from dataclasses import dataclass
from typing import Optional
from pysrc.util.types import Asset
from enum import Enum


class SystemStatus(Enum):
    ONLINE = 1
    MAINTENANCE = 2
    CANCEL_ONLY = 3
    POST_ONLY = 4


@dataclass
class SystemStatusResponse:
    status: SystemStatus
    timestamp: str


class AssetStatus(Enum):
    ENABLED = 1
    DEPOSIT_ONLY = 2
    WITHDRAWAL_ONLY = 3
    FUNDING_TEMPORARILY_DISABLED = 4


@dataclass
class AssetInfo:
    asset: Asset
    asset_name: str
    altname: str
    decimals: int
    collateral_value: Optional[float]
    status: AssetStatus


@dataclass
class AssetPairInfo:
    altname: str
    wsname: Optional[str]
    aclass_base: str
    base: str
    aclass_quote: str
    quote: str


class TradeableAssetPairParam(Enum):
    INFO = 1
    LEVERAGE = 2
    FEES = 3
    MARGIN = 4


@dataclass
class OHLCTick:
    time: int
    open: str
    high: str
    low: str
    close: str
    vwap: str
    volume: str
    count: int


@dataclass
class OHLCData:
    asset: Asset
    ticks: list[OHLCTick]
    last: Optional[int]


class SpreadMessage:
    def __init__(
        self,
        time: int,
        feedcode: str,
        bid: float,
        ask: float,
    ):
        self.time = time
        self.feedcode = feedcode
        self.bid = bid
        self.ask = ask
