import numpy as np
import struct
from pathlib import Path
from datetime import date, timedelta
from pyzstd import compress, decompress, CParameter, ZstdFile
from typing import Optional, Generator

from pysrc.data_handlers.kraken.historical.base_data_handler import BaseDataHandler
from pysrc.adapters.messages import SnapshotMessage
from pysrc.util.types import Market


class SnapshotsDataHandler(BaseDataHandler):
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
        with ZstdFile(input_path, "rb") as f:
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

    def _update_message_from_stream(self, file: ZstdFile) -> Optional[SnapshotMessage]:
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
        self, asset: str, since: date, until: Optional[date]
    ) -> Generator[SnapshotMessage, None, None]:
        asset_path = self.resource_path / asset
        if not asset_path.exists():
            raise ValueError(f"No directory for `{asset}` found in resource path")

        if not until:
            until = date.today()

        file_paths = []
        for i in range((until - since).days):
            cur = since + timedelta(days=i)
            cur_file_name = cur.strftime("%m_%d_%Y.bin")
            cur_path = asset_path / cur_file_name
            if not cur_path.exists():
                raise ValueError(f"Expected file '{cur_path}' does not exist")
            file_paths.append(cur_path)

        for cur_path in file_paths:
            with ZstdFile(cur_path, "rb") as f:
                while True:
                    snapshot = self._update_message_from_stream(f)
                    if not snapshot:
                        break
                    yield snapshot
