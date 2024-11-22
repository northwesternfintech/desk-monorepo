from pysrc.adapters.messages import SnapshotMessage, TradeMessage
from pysrc.signal.base_feature_generator import BaseFeatureGenerator
from pysrc.util.types import Asset


class TestFeatureGenerator(BaseFeatureGenerator):
    __test__ = False
    features = ["a", "b", "c"]
    asset = Asset.BTC

    def __init__(self) -> None:
        pass

    def on_tick(
        self,
        snapshots: dict[str, SnapshotMessage],
        trades: dict[str, list[TradeMessage]],
    ) -> dict[Asset, dict[str, list[float]]]:
        output = {}
        output[self.asset] = {"a": [7.0], "b": [7.0], "c": [7.0]}
        return output
