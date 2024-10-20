from typing import Optional, List
from pysrc.util.types import Asset
from enum import Enum


class SystemStatus(Enum):
    ONLINE = 1
    MAINTENANCE = 2
    CANCEL_ONLY = 3
    POST_ONLY = 4


class SystemStatusResponse:
    def __init__(self, status: SystemStatus, timestamp: str):
        self.status = status
        self.timestamp = timestamp


class AssetStatus(Enum):
    ENABLED = 1
    DEPOSIT_ONLY = 2
    WITHDRAWAL_ONLY = 3
    FUNDING_TEMPORARILY_DISABLED = 4


class AssetInfo:
    def __init__(
        self,
        asset: Asset,
        asset_name: str,
        altname: str,
        decimals: int,
        collateral_value: Optional[float],
        status: AssetStatus,
    ):
        self.asset = asset
        self.asset_name = asset_name
        self.altname = altname
        self.decimals = decimals
        self.collateral_value = collateral_value
        self.status = status


class AssetPairInfo:
    def __init__(
        self,
        altname: str,
        wsname: Optional[str],
        aclass_base: str,
        base: str,
        aclass_quote: str,
        quote: str,
    ):
        self.altname = altname
        self.wsname = wsname
        self.aclass_base = aclass_base
        self.base = base
        self.aclass_quote = aclass_quote
        self.quote = quote


class TradeableAssetPairParam(Enum):
    INFO = 1
    LEVERAGE = 2
    FEES = 3
    MARGIN = 4


class OHLCTick:
    def __init__(
        self,
        time: int,
        open: str,
        high: str,
        low: str,
        close: str,
        vwap: str,
        volume: str,
        count: int,
    ):
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.vwap = vwap
        self.volume = volume
        self.count = count


class OHLCData:
    def __init__(self, asset: Asset, ticks: List[OHLCTick], last: Optional[int]):
        self.asset = asset
        self.ticks = ticks
        self.last = last


class SpreadMessage:
    def __init__(self, time: int, feedcode: str, bid: float, ask: float):
        self.time = time
        self.feedcode = feedcode
        self.bid = bid
        self.ask = ask
