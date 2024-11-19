import numpy as np
import struct
from io import BufferedIOBase
from pathlib import Path
from datetime import timedelta, date
from pyzstd import compress, decompress, CParameter, ZstdFile, EndlessZstdDecompressor
from typing import Optional, Generator

from pysrc.data_handlers.kraken.historical.base_data_handler import BaseDataHandler
from pysrc.adapters.messages import TradeMessage
from pysrc.util.types import Market, OrderSide


class TradesDataHandler(BaseDataHandler):
    def __init__(self, resource_path: Path) -> None:
        self.resource_path = resource_path
        self._np_dtype = [("time", "u8"), ("price", "f4"), ("volume", "f4")]
        self._zstd_options = {CParameter.compressionLevel: 10}
        self._record_size = 16

    def _compress(self, data: bytes, output_path: Path) -> None:
        with open(output_path, "wb") as f:
            f.write(compress(data, level_or_option=self._zstd_options))

    def _decompress(self, input_path: Path) -> bytes:
        with open(input_path, "rb") as f:
            return decompress(f.read())

    def _serialize_csv(self, csv_path: Path) -> Path:
        arr = np.loadtxt(csv_path, delimiter=",", dtype=self._np_dtype)
        new_file_path = csv_path.with_suffix(".bin")
        self._compress(arr.tobytes(), new_file_path)
        return new_file_path

    def _trades_to_numpy(self, trades: list[TradeMessage]) -> np.ndarray:
        arr = np.empty(len(trades), dtype=self._np_dtype)
        for i, trade in enumerate(trades):
            arr[i] = (trade.time, trade.price, trade.quantity)
        return arr

    def read_file(self, input_path: Path) -> list[TradeMessage]:
        arr = np.frombuffer(self._decompress(input_path), dtype=self._np_dtype)
        asset = input_path.parent.name
        trades = []
        for trade_data in arr:
            time, price, volume = trade_data
            trade = TradeMessage(
                time, asset, 1, price, volume, OrderSide.BID, Market.KRAKEN_SPOT
            )
            trades.append(trade)
        return trades

    def write_to_file(self, output_path: Path, data: list[TradeMessage]) -> None:
        arr = self._trades_to_numpy(data)
        self._compress(arr.tobytes(), output_path)

    def _decompress_bytes(
        self, decompressor: EndlessZstdDecompressor, f: BufferedIOBase, output_size: int
    ) -> bytes:
        out = b""
        while len(out) < output_size:
            if decompressor.needs_input:
                f_data = f.read(1024**2)
                if not f_data:
                    break
            else:
                f_data = b""
            out += decompressor.decompress(f_data, max_length=output_size)
        return out

    def _trade_message_from_stream(
        self, decompressor: EndlessZstdDecompressor, f: BufferedIOBase, asset: str
    ) -> Optional[TradeMessage]:
        raw_data = self._decompress_bytes(decompressor, f, self._record_size)
        if not raw_data:
            return None
        elif len(raw_data) < self._record_size:
            raise ValueError("Failed to read data from stream")

        time = struct.unpack("Q", raw_data[0:8])[0]
        price = struct.unpack("f", raw_data[8:12])[0]
        volume = struct.unpack("f", raw_data[12:16])[0]

        return TradeMessage(
            time, asset, 1, price, volume, OrderSide.BID, Market.KRAKEN_SPOT
        )

    def stream_data(
        self, asset: str, since: date, until: Optional[date]
    ) -> Generator[TradeMessage, None, None]:
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

        decompressor = EndlessZstdDecompressor()
        for cur_path in file_paths:
            with open(cur_path, "rb") as f:
                while True:
                    trade = self._trade_message_from_stream(decompressor, f, asset)
                    if not trade:
                        break
                    yield trade

    def _trade_message_from_stream_2(
        self, file: ZstdFile, asset: str
    ) -> Optional[TradeMessage]:
        raw_data = file.read(self._record_size)
        if not raw_data:
            return None
        elif len(raw_data) < self._record_size:
            raise ValueError("Failed to read data from stream")

        time = struct.unpack("Q", raw_data[0:8])[0]
        price = struct.unpack("f", raw_data[8:12])[0]
        volume = struct.unpack("f", raw_data[12:16])[0]

        return TradeMessage(
            time, asset, 1, price, volume, OrderSide.BID, Market.KRAKEN_SPOT
        )

    def stream_data_2(
        self, asset: str, since: date, until: Optional[date]
    ) -> Generator[TradeMessage, None, None]:
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
                    trade = self._trade_message_from_stream_2(f, asset)
                    if not trade:
                        break
                    yield trade
