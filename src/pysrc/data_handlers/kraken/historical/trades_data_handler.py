import numpy as np
import struct
from pathlib import Path
from pyzstd import decompress, CParameter, ZstdFile, ZstdCompressor
from typing import Optional, Generator

from pysrc.data_handlers.kraken.historical.base_data_handler import BaseDataHandler
from pysrc.adapters.kraken.asset_mappings import asset_to_kraken, kraken_to_asset
from pysrc.adapters.messages import TradeMessage
from pysrc.util.types import Market, OrderSide, Asset


class TradesDataHandler(BaseDataHandler):
    def __init__(self, resource_path: Path) -> None:
        self.resource_path = resource_path
        self._np_dtype = [
            ("time", "u8"),
            ("price", "f4"),
            ("volume", "f4"),
            ("side_val", "u1"),
        ]
        self._record_size = 17
        self._zstd_options = {CParameter.compressionLevel: 10}

    def _compress(self, data: bytes, output_path: Path) -> None:
        compressor = ZstdCompressor(level_or_option=self._zstd_options)
        with open(output_path, "wb") as f:
            f.write(compressor.compress(data, ZstdCompressor.FLUSH_FRAME))

    def _decompress(self, input_path: Path) -> bytes:
        with open(input_path, "rb") as f:
            return decompress(f.read())

    def _trades_to_numpy(self, trades: list[TradeMessage]) -> np.ndarray:
        arr = np.empty(len(trades), dtype=self._np_dtype)
        for i, trade in enumerate(trades):
            arr[i] = (trade.time, trade.price, trade.quantity, trade.side.value)
        return arr

    def read(self, input_path: Path) -> list[TradeMessage]:
        if not input_path.exists():
            raise ValueError(f"Expected file '{input_path}' does not exist")
        trades = []
        asset = kraken_to_asset(input_path.parent.name)
        with ZstdFile(input_path, "rb") as f:
            while True:
                trade = self._trade_message_from_stream(f, asset)
                if not trade:
                    break
                trades.append(trade)
        return trades

    def write(self, output_path: Path, data: list[TradeMessage]) -> None:
        out = b""
        for trade in data:
            out += trade.to_bytes()
        self._compress(out, output_path)

    def write_2(self, output_path: Path, data: list[TradeMessage]) -> None:
        arr = self._trades_to_numpy(data)
        self._compress(arr.tobytes(), output_path)

    def _trade_message_from_stream(
        self, file: ZstdFile, asset: Asset
    ) -> Optional[TradeMessage]:
        raw_data = file.read(self._record_size)
        if not raw_data:
            return None
        elif len(raw_data) < self._record_size:
            raise ValueError("Failed to read data from stream")

        time, price, quantity, side_val = struct.unpack("=QffB", raw_data)

        return TradeMessage(
            time,
            asset_to_kraken(asset),
            1,
            price,
            quantity,
            OrderSide(side_val),
            Market.KRAKEN_SPOT,
        )

    def stream_read(self, input_path: Path) -> Generator[TradeMessage, None, None]:
        if not input_path.exists():
            raise ValueError(f"Expected file '{input_path}' does not exist")
        asset = kraken_to_asset(input_path.parent.name)
        with ZstdFile(input_path, "rb") as f:
            while True:
                trade = self._trade_message_from_stream(f, asset)
                if not trade:
                    break
                yield trade


# def csv_to_bytes() -> None:
#     csv_path = Path(__file__).parent / "resources/trades/XADAZUSD/XADAZUSD.csv"
#     np_dtype = [("time", "u8"), ("price", "f4"), ("volume", "f4")]
#     arr = np.loadtxt(csv_path, delimiter=",", dtype=np_dtype)

#     new_dtype = [("time", "u8"), ("price", "f4"), ("volume", "f4"), ("side_val", "u1")]
#     new_arr = np.ones(len(arr), dtype=new_dtype)
#     new_arr["time"] = arr["time"]
#     new_arr["price"] = arr["price"]
#     new_arr["volume"] = arr["volume"]

#     handler = TradesDataHandler(Path(__file__))
#     handler._compress(new_arr.tobytes(), csv_path.with_suffix(".bin"))


# def test_read_1() -> None:
#     resource_path = Path(__file__).parent / "resources/trades/XADAZUSD"
#     handler = TradesDataHandler(resource_path)
#     trades = handler.read_file(resource_path / "XADAZUSD.bin")


# def test_read_2() -> None:
#     resource_path = Path(__file__).parent / "resources/trades/XADAZUSD"
#     handler = TradesDataHandler(resource_path)
#     trades = handler.read_file_2(resource_path / "XADAZUSD.bin")


# def test_write_1() -> None:
#     resource_path = Path(__file__).parent / "resources/trades/XADAZUSD"
#     handler = TradesDataHandler(resource_path)
#     trades = handler.read_file(resource_path / "XADAZUSD.bin")
#     print("Read done!")
#     print(len(trades))
#     handler.write_to_file(resource_path / "test.bin", trades[:500_000])


# def test_write_2() -> None:
#     resource_path = Path(__file__).parent / "resources/trades/XADAZUSD"
#     handler = TradesDataHandler(resource_path)
#     trades = handler.read_file(resource_path / "XADAZUSD.bin")
#     print("Read done!")
#     handler.write_to_file_2(resource_path / "test.bin", trades[:100_000])


# if __name__ == "__main__":

# csv_to_bytes()
# test_read_1() # hyperfine: 4.793 s ±  0.088 s
# test_read_2() # hyperfine: 9.286 s ±  0.224 s
# test_write_1() # hyperfine: 7.028 s ±  0.087 s
# test_write_2() # hyperfine: 4.920 s ±  0.139 s
