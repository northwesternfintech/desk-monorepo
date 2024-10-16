class KrakenFutureClient:
    def __init__(
        self, base_url: str = "https://futures.kraken.com/derivatives/api/v3/"
    ):
        self.base_url = base_url
