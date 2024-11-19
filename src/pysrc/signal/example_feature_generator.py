from pysrc.adapters.messages import SnapshotMessage, TradeMessage
from pysrc.util.types import Asset
from pysrc.signal.base_feature_generator import BaseFeatureGenerator
from typing import override


class ExampleFeatureGenerator(BaseFeatureGenerator):
    order_features = ["open", "high", "low", "close"]
    assets = [Asset.BTC, Asset.ETH, Asset.ADA, Asset.SOL, Asset.DOGE]

    def __init__(self) -> None:
        pass

    def compute_ohlc(self, trades: list[TradeMessage]) -> list[float]:
        if not trades:
            return [0.0, 0.0, 0.0, 0.0]
        prices = [trade.price for trade in trades]
        open_price = prices[0]
        high_price = max(prices)
        low_price = min(prices)
        close_price = prices[-1]
        return [open_price, high_price, low_price, close_price]

    @override
    def on_tick(
        self,
        snapshots: dict[str, SnapshotMessage],
        trades: dict[str, list[TradeMessage]],
    ) -> dict[Asset, dict[str, list[float]]]:
        output = {}
        for asset in self.assets:
            feedcode = asset.name
            asset_trades = trades.get(feedcode, [])
            features = self.compute_ohlc(asset_trades)
            output[asset] = {"features": features}
        # ["open", "high", "low", "close"]
        return output
