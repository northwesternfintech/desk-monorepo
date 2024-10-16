import requests

from pysrc.adapters.kraken.containers import Spread, TickerInfo
from pysrc.adapters.messages import SnapshotMessage, TradeMessage
from pysrc.util.types import Asset

class KrakenClient:
    def __init__(self, base_url: str = "https://api.kraken.com/0/public/", currenecy: str = "USDT"):
        self._base_url = base_url
        self._currency = currenecy

    def _check_errors(self, api_route: str, error: list[str]) -> None:
        if error:
            raise RuntimeError(f"Call to {api_route} failed with {error}")
        
    def get_order_book(self, asset: Asset) -> SnapshotMessage:
        pass

    def get_trades_since(self, asset: Asset, since: str) -> list[TradeMessage]:
        pass

    def get_next_trades(self, asset: Asset) -> list[TradeMessage]:
        pass

    def get_spread_since(self, asset: Asset, since: str) -> list[Spread]:
        pass

    def get_next_spread(self, asset: Asset) -> list[Spread]:
        pass

    def get_ticker_info(self, asset: Asset) -> TickerInfo:
        pass

    def get_ohlc_since(self, asset: Asset, interval: int, since: str):
        pass

    def get_next_ohlc(self, asset: Asset, interval: int):
        pass
        
