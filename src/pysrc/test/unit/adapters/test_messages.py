from pysrc.adapters.messages import SnapshotMessage
from pysrc.util.types import Market
import io


def test_snapshot_message_ctor() -> None:
    msg = SnapshotMessage(25, "BTC", [["15", "5"], ["16", "0"]], [], Market.KRAKEN_SPOT)
    assert len(msg.get_bids()) == 1
    msg = SnapshotMessage(25, "BTC", [["15", "5"], ["16", "2"]], [], Market.KRAKEN_SPOT)
    assert len(msg.get_bids()) == 2
    assert len(msg.get_asks()) == 0


def test_snapshot_serialization() -> None:
    msg = SnapshotMessage(
        25,
        "BTC",
        [["15", "5"], ["16", "0"]],
        [["16", "0"], ["17", "1"], ["18", "2"], ["19", "3"]],
        Market.KRAKEN_SPOT,
    )
    new_msg = SnapshotMessage.from_bytes(msg.to_bytes())

    assert msg.time == new_msg.time
    assert msg.feedcode == new_msg.feedcode
    assert msg.market == new_msg.market
    assert msg.bids == new_msg.bids
    assert msg.asks == new_msg.asks
