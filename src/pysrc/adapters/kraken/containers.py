from enum import Enum
from pysrc.util.types import Asset


class Spread:
    def __init__(self,
                 asset: Asset,
                 time: int,
                 feedcode: str,
                 bid_price: str,
                 ask_price: str):
        self.asset = asset
        self.time = time
        self.feedcode = feedcode
        self.bid_price: float = float(bid_price)
        self.ask_price: float = float(ask_price)

class AssetStatus(Enum):
    ENABLED = 0
    DEPOSIT_ONLY = 1
    WITHDRAWAL_ONLY = 1
    FUNDING_TEMPORARILY_DISABLED = 2

class AssetInfo:
    def __init__(self,
                 asset: Asset,
                 asset_name: str,
                 altname: str,
                 decimals: int,
                 collateral_value: float,
                 status: AssetStatus):
        pass

class TickerInfo:
    def __init__(self,
                 asset: Asset,
                 ask,
                 ask_volume,
                 bid,
                 bid_volume,
                 trade_closed_price,
                 trade_closed_lot_volume,
                 volume_today,
                 volume_last_24_hours,):
        # There's other stuff, not sure if we care about any/all of it
        # https://docs.kraken.com/api/docs/rest-api/get-ticker-information/