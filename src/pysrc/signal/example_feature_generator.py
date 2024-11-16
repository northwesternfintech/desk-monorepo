from pysrc.adapters.messages import SnapshotMessage, TradeMessage
from pysrc.util.types import Asset
from pysrc.signal.base_feature_generator import BaseFeatureGenerator


class OHLCFeatureGenerator(BaseFeatureGenerator):
    def __init__(self) -> None:
        self.ohlc_data: dict[Asset, dict[str, float]] = {}

    def calculate_ohlc(self, trades: list[TradeMessage]) -> dict[str, float]:
        if not trades:
            # Return NaNs for missing values
            return {
                "open": float("nan"),
                "high": float("nan"),
                "low": float("nan"),
                "close": float("nan"),
            }

        prices = [trade.price for trade in trades]

        return {
            "open": prices[0],
            "high": max(prices),
            "low": min(prices),
            "close": prices[-1],
        }

    def on_tick(
        self, snapshots: dict[str, SnapshotMessage], trades: dict[str, TradeMessage]
    ) -> dict[Asset, dict[str, list[float]]]:
        result: dict[Asset, dict[str, list[float]]] = {}

        for asset_str, trade in trades.items():
            asset = Asset(asset_str)
            trade_list = [trade]

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
                    "open": [float("nan")],
                    "high": [float("nan")],
                    "low": [float("nan")],
                    "close": [float("nan")],
                }

        return result
