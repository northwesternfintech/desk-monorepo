from pysrc.adapters.messages import SnapshotMessage
from pysrc.util.types import Market


def test_snapshot_message_ctor() -> None:
    msg = SnapshotMessage(25, "BTC", [["15", "5"], ["16", "0"]], [], Market.KRAKEN_SPOT)
    assert len(msg.get_bids()) == 1
    msg = SnapshotMessage(25, "BTC", [["15", "5"], ["16", "2"]], [], Market.KRAKEN_SPOT)
    assert len(msg.get_bids()) == 2
    assert len(msg.get_asks()) == 0
