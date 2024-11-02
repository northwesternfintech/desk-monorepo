from pysrc.adapters.messages import SnapshotMessage, TradeMessage
from pysrc.util.types import Asset


class BaseFeatureGenerator:
    def __init__(self) -> None:
        # put any state that you need here.
        raise NotImplementedError

    def on_tick(
        self, snapshots: dict[str, SnapshotMessage], trades: dict[str, TradeMessage]
    ) -> dict[Asset, dict[str, list[float]]]:
        # compute all features. BE CERTAIN that the output order matches the order of your trained model.
        raise NotImplementedError
