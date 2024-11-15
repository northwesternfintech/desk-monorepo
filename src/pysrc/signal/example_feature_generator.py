from pysrc.adapters.messages import SnapshotMessage, TradeMessage
from pysrc.util.types import Asset
from pysrc.signal.base_feature_generator import BaseFeatureGenerator


class OHLCFeatureGenerator(BaseFeatureGenerator):
    def __init__(self) -> None:
        self.ohlc_data = {}

    def calculate_ohlc(self, trades: list[TradeMessage]) -> dict[str, float]:
        if not trades:
            return {"open": None, "high": None, "low": None, "close": None}

        prices = [trade.price for trade in trades]

        return {
            "open": prices[0],
            "high": max(prices),
            "low": min(prices),
            "close": prices[-1],
        }

    def on_tick(
        self, snapshots: dict[str, SnapshotMessage], trades: dict[Asset, list[TradeMessage]]
    ) -> dict[Asset, dict[str, list[float]]]:
        result = {}

        for asset, trade_list in trades.items():
            if trade_list:
                ohlc_values = self.calculate_ohlc(trade_list)
                result[asset] = {
                    "open": [ohlc_values["open"]],
                    "high": [ohlc_values["high"]],
                    "low": [ohlc_values["low"]],
                    "close": [ohlc_values["close"]],
                }
            else:
                result[asset] = {
                    "open": [None],
                    "high": [None],
                    "low": [None],
                    "close": [None],
                }

        return result
