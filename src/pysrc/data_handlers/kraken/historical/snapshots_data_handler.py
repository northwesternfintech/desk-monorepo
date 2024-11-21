import numpy as np
import struct
from pathlib import Path
from pyzstd import ZstdFile, CParameter, ZstdCompressor
from typing import Optional, Generator

from pysrc.data_handlers.kraken.historical.base_data_handler import BaseDataHandler
from pysrc.adapters.messages import SnapshotMessage
from pysrc.util.types import Market


class SnapshotsDataHandler(BaseDataHandler):
    def __init__(self) -> None:
        self._metadata_size = 24
        self._zstd_options = {CParameter.compressionLevel: 10}

    def read(self, input_path: Path) -> list[SnapshotMessage]:
        if not input_path.exists():
            raise ValueError(f"Expected file '{input_path}' does not exist")
        snapshots = []
        with ZstdFile(input_path, "rb") as f:
            while True:
                snapshot = self._snapshot_message_from_stream(f)
                if not snapshot:
                    break
                snapshots.append(snapshot)
        return snapshots

    def write(self, output_path: Path, data: list[SnapshotMessage]) -> None:
        compressor = ZstdCompressor(level_or_option=self._zstd_options)
        out = b""
        with open(output_path, "wb") as f:
            for snapshot in data:
                out = snapshot.to_bytes()
                f.write(compressor.compress(out))
            f.write(compressor.flush())

    def _snapshot_message_from_stream(
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

    def stream_read(self, input_path: Path) -> Generator[SnapshotMessage, None, None]:
        if not input_path.exists():
            raise ValueError(f"Expected file '{input_path}' does not exist")
        with ZstdFile(input_path, "rb") as f:
            while True:
                snapshot = self._snapshot_message_from_stream(f)
                if not snapshot:
                    break
                yield snapshot
