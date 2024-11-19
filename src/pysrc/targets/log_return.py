import numpy as np
from collections import deque
import time

from pysrc.util.types import Asset
from pysrc.adapters.kraken.spot.kraken_client import KrakenClient
from pysrc.adapters.messages import SnapshotMessage


class TargetLogReturn:
    def __init__(self, time_delay: int, asset: Asset) -> None:
        self._time_delay = time_delay
        self._asset = asset
        self._buffer: deque[SnapshotMessage] = deque(maxlen=time_delay)
        self._client = KrakenClient()

        # initialize the buffer to be time delayed
        for _ in range(time_delay):
            snapshot = self._client.get_order_book(asset)
            self._buffer.append(snapshot)
            time.sleep(1)

    def update(self, snapshot: SnapshotMessage) -> None:
        self._buffer.append(snapshot)

        while self._buffer and (
            self._buffer[0].time - self._buffer[-1].time > self._time_delay
        ):
            self._buffer.popleft()

    def compute_midprice(self, snapshot: SnapshotMessage) -> float:
        return float((snapshot.bids[0][0] + snapshot.asks[0][0]) / 2)

    def next(self) -> float:
        self.update(self._client.get_order_book(self._asset))

        left_midprice = self.compute_midprice(self._buffer[0])
        right_midprice = self.compute_midprice(self._buffer[-1])

        return float(np.log(right_midprice / left_midprice))
