import numpy as np
import struct
from pathlib import Path
from datetime import datetime, timedelta
from pyzstd import compress, decompress, CParameter, ZstdFile
from typing import Optional, Generator

from pysrc.file_handlers.kraken.historical.base_handler import BaseHandler
from pysrc.adapters.messages import SnapshotMessage
from pysrc.util.types import Market


class RawUpdatesHandler(BaseHandler):
    
    def __init__(self, resource_path: Path) -> None:
        self.resource_path = resource_path
        self._zstd_options = {CParameter.compressionLevel: 10}
        self._metadata_size = 24


    def _compress(self, data: bytes, output_path: Path) -> None:
        with open(output_path, "wb") as f:
            f.write(compress(data, level_or_option=self._zstd_options))


    def _decompress(self, input_path: Path) -> bytes:
        with open(input_path, "rb") as f:
            return decompress(f.read())


    def read_file(self, input_path: Path) -> list[SnapshotMessage]:
        snapshots = []
        with ZstdFile(input_path, 'rb') as f:
            while True:
                snapshot = self._update_message_from_stream(f)
                if not snapshot:
                    break
                snapshots.append(snapshot)
        return snapshots
    

    def write_to_file(self, output_path: Path, data: list[SnapshotMessage]) -> None:
        out = b""
        for snapshot in data:
            out += snapshot.to_bytes()
        self._compress(out, output_path)


    def _update_message_from_stream(
        self, file: ZstdFile
    ) -> Optional[SnapshotMessage]:
        
        packed_metadata = file.read(self._metadata_size)
        if not packed_metadata:
            return None
        elif len(packed_metadata) < 24:
            raise ValueError("Failed to read metadata from stream")

        time, market_value, feedcode_size, bids_size, asks_size = struct.unpack(
            "QIIII", packed_metadata
        )

        feedcode_data = file.read(feedcode_size)
        if len(feedcode_data) < feedcode_size:
            raise ValueError("Failed to read feedcode from stream")

        bids_bytes = file.read(bids_size)
        if len(bids_bytes) < bids_size:
            raise ValueError("Failed to read bids from stream")
        bids = np.frombuffer(bids_bytes)

        asks_bytes = file.read(asks_size)
        if len(asks_bytes) < asks_size:
            raise ValueError("Failed to read asks from stream")
        asks = np.frombuffer(asks_bytes)

        return SnapshotMessage(
            time=time,
            feedcode=feedcode_data.decode(),
            market=Market(market_value),
            bids=bids.reshape((-1, 2)).tolist(),
            asks=asks.reshape((-1, 2)).tolist(),
        )
    

    def stream_data(
        self, asset: str, since: datetime, until: Optional[datetime]
    ) -> Generator[SnapshotMessage, None, None]:
        
        asset_path = self.resource_path / asset
        if not asset_path.exists():
            raise ValueError(f"No directory for `{asset}` found in resource path")

        if not until:
            until = datetime.today()

        file_paths = []
        for i in range((until - since).days):
            cur = since + timedelta(days=i)
            cur_file_name = cur.strftime("%m_%d_%Y.bin")
            cur_path = asset_path / cur_file_name
            if not cur_path.exists():
                raise ValueError(f"Expected file '{cur_path}' does not exist")
            file_paths.append(cur_path)

        for cur_path in file_paths:
            with ZstdFile(cur_path, 'rb') as f:
                while True:
                    snapshot = self._update_message_from_stream(f)
                    if not snapshot:
                        break
                    yield snapshot



def run_tests(asset: str) -> None:

    resource_path = Path(__file__).parent / "resources" / "snapshots"
    handler = RawUpdatesHandler(resource_path)

    snapshots = [
        SnapshotMessage(
            time=1,
            feedcode=asset,
            market=Market.KRAKEN_USD_FUTURE,
            bids=[],
            asks=[[1.0, 2.0]],
        ),
        SnapshotMessage(
            time=2,
            feedcode=asset,
            market=Market.KRAKEN_USD_FUTURE,
            bids=[[3.0, 4.0], [5.0, -6.0], [68717.5, -3000.0]],
            asks=[[1.0, 2.0], [68717.5, -3000.0]],
        ),
        SnapshotMessage(
            time=10,
            feedcode=asset,
            market=Market.KRAKEN_USD_FUTURE,
            bids=[[3.0, 4.0], [5.0, -6.0], [68717.5, -3000.0], [7.0, -8.0]],
            asks=[[1.0, 2.0], [68717.5, -3000.0]],
        ),
    ]

    handler.write_to_file(resource_path / asset / f"{asset}.bin", snapshots)
    handler.write_to_file(resource_path / asset / "11_11_2024.bin", snapshots)
    handler.write_to_file(resource_path / asset / "11_12_2024.bin", snapshots)
    handler.write_to_file(resource_path / asset / "11_13_2024.bin", snapshots)
    handler.write_to_file(resource_path / asset / "11_14_2024.bin", snapshots)
    handler.write_to_file(resource_path / asset / "11_15_2024.bin", snapshots)

    read_snapshots = handler.read_file(resource_path / asset / f"{asset}.bin")
    for snapshot in read_snapshots:
        print(snapshot.time, snapshot.bids, snapshot.asks)
    print("")

    gen = handler.stream_data(
        "BONKUSD",
        datetime(year=2024, month=11, day=11),
        until=datetime(year=2024, month=11, day=16),
    )

    i = 0
    while True:
        try:
            snapshot = next(gen)
            i += 1
            print(i, snapshot.time, snapshot.bids, snapshot.asks)
        except StopIteration:
            break



if __name__ == "__main__":
    run_tests("BONKUSD")