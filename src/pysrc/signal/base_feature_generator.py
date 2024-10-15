from pysrc.adapters.messages import SnapshotMessage, TradeMessage


class BaseFeatureGenerator:
    def __init__(self):
        # put any state that you need here.
        raise NotImplementedError

    def on_tick(
        self, snapshots: dict[str, SnapshotMessage], trades: dict[str, TradeMessage]
    ) -> list[float]:
        # compute all features. BE CERTAIN that the output order matches the order of your trained model.
        raise NotImplementedError
