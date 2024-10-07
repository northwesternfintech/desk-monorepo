from pysrc.util.types import Market


class Instrument:
    def __init__(self, market: Market, feedcode: str):
        self.market = market
        self.feedcode = feedcode

    def get_market(self) -> Market:
        return self.market

    def get_feedcode(self) -> str:
        return self.feedcode
