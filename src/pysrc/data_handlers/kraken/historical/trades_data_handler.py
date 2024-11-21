import numpy as np
import struct
from pathlib import Path
from pyzstd import CParameter, ZstdFile, ZstdCompressor
from typing import Optional, Generator

from pysrc.data_handlers.kraken.historical.base_data_handler import BaseDataHandler
from pysrc.adapters.kraken.asset_mappings import asset_to_kraken, kraken_to_asset
from pysrc.adapters.messages import TradeMessage
from pysrc.util.types import Market, OrderSide, Asset


class TradesDataHandler(BaseDataHandler):
    def __init__(self) -> None:
        self._np_dtype = [
            ("time", "u8"),
            ("price", "f4"),
            ("volume", "f4"),
            ("side_val", "u1"),
        ]
        self._record_size = 17
        self._zstd_options = {CParameter.compressionLevel: 10}

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
        compressor = ZstdCompressor(level_or_option=self._zstd_options)
        out = b""
        with open(output_path, "wb") as f:
            for trade in data:
                out = trade.to_bytes()
                f.write(compressor.compress(out))
            f.write(compressor.flush())

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
