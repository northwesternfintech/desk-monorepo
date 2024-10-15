from pysrc.util.types import Market, OrderSide


class SnapshotMessage:
    def __init__(
        self,
        time: int,
        feedcode: str,
        bids: list[list[str]],
        asks: list[list[str]],
        market: Market,
    ):
        self.time = time
        self.feedcode = feedcode
        self.bids: list[tuple[float, float]] = []
        self.asks: list[tuple[float, float]] = []
        for price, volume in bids:
            volume_float = float(volume)
            if volume_float != 0.0:
                self.bids.append((float(price), volume_float))

        for price, volume in asks:
            volume_float = float(volume)
            if volume_float != 0.0:
                self.asks.append((float(price), volume_float))

    def get_bids(self) -> list[tuple[float, float]]:
        return self.bids

    def get_asks(self) -> list[tuple[float, float]]:
        return self.asks


class TradeMessage:
    def __init__(
        self,
        time: int,
        feedcode: str,
        quantity: int,
        n_trades: int,
        side: OrderSide,
        market: Market,
    ):
        self.time = time
        self.feecode = feedcode
        self.quantity = quantity
        self.n_trades = n_trades
        self.side = side
        self.market = market
