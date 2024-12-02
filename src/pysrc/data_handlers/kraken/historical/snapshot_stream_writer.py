from io import BufferedWriter
from pathlib import Path
from typing import Generator, Optional

from pyzstd import CParameter, ZstdCompressor

from pysrc.adapters.messages import SnapshotMessage
from pysrc.util.exceptions import DIE
from pysrc.util.historical_data_utils import check_historical_data_filepath


class SnapshotStreamWriter:
    def __init__(self) -> None:
        self._zstd_options = {CParameter.compressionLevel: 10}
        self._file: Optional[BufferedWriter] = None
        self._compressor: Optional[ZstdCompressor] = None

    def open(self, input_path: Path) -> None:
        if not check_historical_data_filepath(input_path, False):
            raise ValueError(f"Invalid input snapshots file path: {input_path}")

        self._file = open(input_path, "wb")
        self._compressor = ZstdCompressor(level_or_option=self._zstd_options)

    def write(self, data: SnapshotMessage) -> None:
        if self._file is None or self._compressor is None:
            DIE("Wrote without opening file")

        self._file.write(self._compressor.compress(data.to_bytes()))

    def flush(self) -> None:
        if self._file is None or self._compressor is None:
            DIE("Flush without opening file")

        self._file.write(self._compressor.flush())

        self._file.close()
        self._file = None
        self._compressor = None

    def stream_read(self, _: Path) -> Generator[SnapshotMessage, None, None]:
        DIE("Class not meant for reading")
