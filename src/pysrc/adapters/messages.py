import struct

import numpy as np

from pysrc.util.types import Market, OrderSide


class SnapshotMessage:
    def __init__(
        self,
        time: int,
        feedcode: str,
        bids: list[list[float]] | list[list[str]],
        asks: list[list[float]] | list[list[str]],
        market: Market,
    ):
        self.time = time
        self.feedcode = feedcode
        self.bids: list[tuple[float, float]] = []
        self.asks: list[tuple[float, float]] = []
        self.market = market
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

    def to_bytes(self) -> bytes:
        bids = np.array(self.bids).tobytes()
        asks = np.array(self.asks).tobytes()

        packed_metadata = struct.pack(
            "QIIII",
            self.time,
            self.market.value,
            len(self.feedcode),
            len(bids),
            len(asks),
        )
        return packed_metadata + str.encode(self.feedcode) + bids + asks

    @staticmethod
    def from_bytes(b: bytes) -> "SnapshotMessage":
        if len(b) < 24:
            raise ValueError("Can't create SnapshotMessage from <24 bytes")

        packed_metadata = b[:24]
        data = b[24:]
        time, market_value, feedcode_size, bids_size, asks_size = struct.unpack(
            "QIIII", packed_metadata
        )

        offset = 0
        feedcode_data = data[:feedcode_size]

        offset += feedcode_size
        bids_data = data[offset : offset + bids_size]

        offset += bids_size
        asks_data = data[offset : offset + asks_size]

        bids = np.frombuffer(bids_data)
        asks = np.frombuffer(asks_data)

        return SnapshotMessage(
            time=time,
            feedcode=feedcode_data.decode(),
            market=Market(market_value),
            bids=bids.reshape((-1, 2)).tolist(),
            asks=asks.reshape((-1, 2)).tolist(),
        )


class TradeMessage:
    def __init__(
        self,
        time: int,
        feedcode: str,
        n_trades: int,
        price: float,
        quantity: float,
        side: OrderSide,
        market: Market,
    ):
        self.time = time
        self.feedcode = feedcode
        self.n_trades = n_trades
        self.quantity = quantity
        self.price = price
        self.side = side
        self.market = market

    def to_bytes(self) -> bytes:
        return struct.pack(
            "=QffB",
            self.time,
            self.price,
            self.quantity,
            self.side.value,
        )

    @staticmethod
    def from_bytes(b: bytes, feedcode: str, market: Market) -> "TradeMessage":
        if len(b) != 17:
            raise ValueError("Can't create TradeMessage from != 17 bytes")
        time, price, quantity, side_val = struct.unpack("=QffB", b)

        return TradeMessage(
            time=time,
            feedcode=feedcode,
            n_trades=1,
            price=price,
            quantity=quantity,
            side=OrderSide(side_val),
            market=market,
        )
