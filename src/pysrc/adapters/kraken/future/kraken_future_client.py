FUTURES_API_LIVE_BASE_URL = "https://futures.kraken.com/derivatives/api/v3/"
FUTURES_API_TESTNET_BASE_URL = "https://demo-futures.kraken.com/derivatives/api/v3/"

from pysrc.adapters.messages import TradeMessage

class KrakenFutureClient:
    def __init__(self, use_live_api: bool = True):
        self.base_url: str = (
            FUTURES_API_LIVE_BASE_URL if use_live_api else FUTURES_API_TESTNET_BASE_URL
        )

    def public_get_history(self, symbol: str, lastTime: int) -> list(TradeMessage):
        pass

    def public_get_orderbook(self, symbol: str) -> Orderbook:
        pass

