from io import RawIOBase
from typing import Optional
from pysrc.util.types import Market, OrderSide
import numpy as np
import struct


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
            raise ValueError("Can't create SnapshotMessage from <16 bytes")

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
            bids=bids.reshape((-1, 2)),
            asks=asks.reshape((-1, 2)),
        )

    # @staticmethod
    # def from_stream(s: RawIOBase) -> Optional['SnapshotMessage']:
    #     packed_metadata = s.read(24)
    #     if not packed_metadata:
    #         return None
    #     elif len(packed_metadata) < 24:
    #         raise ValueError("Failed to read metadata from stream")

    #     time, market_value, feedcode_size, bids_size, asks_size = struct.unpack("QIIII", packed_metadata)

    #     feedcode_data = s.read(feedcode_size)
    #     if not feedcode_data:
    #         raise ValueError("Failed to read feedcode from stream")

    #     bids = s.read(bids_size)
    #     if not bids:
    #         raise ValueError("Failed to read bids from stream")

    #     asks = s.read(asks_size)
    #     if not asks:
    #         raise ValueError("Failed to read asks from stream")

    #     return SnapshotMessage(
    #         time=time,
    #         feedcode=feedcode_data.decode(),
    #         market=Market(market_value),
    #         bids=bids.reshape((-1, 2)),
    #         asks=asks.reshape((-1, 2))
    #     )


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
