from datetime import date
from pathlib import Path

import numpy as np
import pytest

from pysrc.adapters.messages import SnapshotMessage
from pysrc.data_handlers.kraken.historical.snapshots_data_handler import (
    SnapshotsDataHandler,
)
from pysrc.data_loaders.tick_snapshots_data_loader import TickSnapshotsDataLoader
from pysrc.util.types import Asset, Market

resource_path = Path(__file__).parent / "resources"


def test_initialization_error() -> None:
    with pytest.raises(ValueError) as msg:
        TickSnapshotsDataLoader(
            resource_path=resource_path,
            asset=Asset.ADA,
            market=Market.KRAKEN_SPOT,
            since=date(year=2024, month=7, day=1),
            until=date(year=2024, month=6, day=1),
        )
    assert (
        str(msg.value)
        == "Dates since (07_01_2024) equal to or later than until (06_01_2024)"
    )

    with pytest.raises(ValueError) as msg:
        TickSnapshotsDataLoader(
            resource_path=resource_path / "lol",
            asset=Asset.ADA,
            market=Market.KRAKEN_SPOT,
            since=date(year=2024, month=6, day=25),
            until=date(year=2024, month=7, day=1),
        )
    assert "Directory for asset snapshots data" in str(
        msg.value
    ) and "doesn't exist" in str(msg.value)

    with pytest.raises(ValueError) as msg:
        TickSnapshotsDataLoader(
            resource_path=resource_path,
            asset=Asset.ADA,
            market=Market.KRAKEN_SPOT,
            since=date(year=2024, month=6, day=1),
            until=date(year=2024, month=7, day=1),
        )
    assert "Expected file" in str(msg.value) and "doesn't exist" in str(msg.value)


def test_get_data_error() -> None:
    loader = TickSnapshotsDataLoader(
        resource_path=resource_path,
        asset=Asset.ADA,
        market=Market.KRAKEN_SPOT,
        since=date(year=2024, month=6, day=25),
        until=date(year=2024, month=7, day=1),
    )

    with pytest.raises(ValueError) as msg:
        loader.get_data(
            since=date(year=2024, month=6, day=1),
            until=date(year=2024, month=7, day=1),
        )
    assert "Expected file" in str(msg.value) and "doesn't exist" in str(msg.value)

    with pytest.raises(ValueError) as msg:
        loader.get_data(
            since=date(year=2024, month=6, day=25),
            until=date(year=2024, month=7, day=2),
        )
    assert "Expected file" in str(msg.value) and "doesn't exist" in str(msg.value)


def test_get_data_and_next_success() -> None:
    start = date(year=2024, month=6, day=26)
    end = date(year=2024, month=6, day=30)
    handler = SnapshotsDataHandler()
    loader = TickSnapshotsDataLoader(
        resource_path=resource_path,
        asset=Asset.ADA,
        market=Market.KRAKEN_SPOT,
        since=start,
        until=end,
    )

    all_snapshots = loader.get_data(start, end)

    target_path = resource_path / "snapshots" / "XADAZUSD" / "test.bin"
    targets = handler.read(target_path)
    targets = [
        target
        for target in targets
        if (target.time >= loader._date_to_timestamp(start))
        and (target.time < loader._date_to_timestamp(end))
    ]

    all_snapshots_idx = 0
    target_idx = 0
    count = 0
    cur_epoch = loader._date_to_timestamp(start)
    if targets[0].time == cur_epoch:
        target_snapshot = targets[0]
    else:
        target_snapshot = SnapshotMessage(
            time=cur_epoch,
            feedcode="XADAZUSD",
            bids=[],
            asks=[],
            market=Market.KRAKEN_SPOT,
        )
        target_idx = -1

    while True:
        snapshot = loader.next()
        if snapshot is None:
            break
        while (target_idx + 1 < len(targets)) and (
            cur_epoch == targets[target_idx + 1].time
        ):
            target_idx += 1
            target_snapshot = targets[target_idx]

        assert snapshot.time == target_snapshot.time
        assert snapshot.bids == target_snapshot.bids
        assert snapshot.asks == target_snapshot.asks
        assert snapshot.feedcode == target_snapshot.feedcode
        assert snapshot.market == target_snapshot.market

        assert snapshot.time == all_snapshots[all_snapshots_idx].time
        assert snapshot.bids == all_snapshots[all_snapshots_idx].bids
        assert snapshot.asks == all_snapshots[all_snapshots_idx].asks
        assert snapshot.feedcode == all_snapshots[all_snapshots_idx].feedcode
        assert snapshot.market == all_snapshots[all_snapshots_idx].market

        all_snapshots_idx += 1
        cur_epoch += 1
        count += 1

    assert count == 60 * 60 * 24 * 4
    assert len(all_snapshots) == 60 * 60 * 24 * 4
