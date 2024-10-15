from pysrc.util.types import Market, OrderSide


class SnapshotMessage:
    def __init__(self, time: int, feedcode: str, bids: list[list[str]], asks: list[list[str]], market: Market):
        self.time = time
        self.feedcode = feedcode
        self.bids: list[tuple[float]] = []
        self.asks: list[tuple[float]] = []
        for price, volume in bids:
            volume = float(volume)
            if volume != 0.0:
                self.bids.append(float(price), volume)

        for price, volume in asks:
            volume = float(volume)
            if volume != 0.0:
                self.asks.append(float(price), volume)

    def get_bids(self) -> list[tuple[float]]:
        return self.bids

    def get_asks(self) -> list[tuple[float]]:
        return self.asks


class TradeMessage:
    def __init__(self, time: int, feedcode: str, quantity: int, n_trades: int, side: OrderSide, market: Market):
        self.time = time
        self.feecode = feedcode
        self.quantity = quantity
        self.n_trades = n_trades
        self.side = side
        self.market = market
