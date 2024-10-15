from pysrc.util.types import Market, Asset


class Instrument:
    def __init__(self, market: Market, asset: Asset):
        self.market = market
        self.asset = asset

    def get_market(self) -> Market:
        return self.market

    def get_asset(self) -> Asset:
        return self.asset
