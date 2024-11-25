from datetime import date
from pathlib import Path

import numpy as np
import pytest

from pysrc.data_handlers.kraken.historical.snapshots_data_handler import (
    SnapshotsDataHandler,
)
from pysrc.data_loaders.raw_snapshots_data_loader import RawSnapshotsDataLoader
from pysrc.util.types import Asset, Market

resource_path = Path(__file__).parent / "resources"


def test_initialization_error() -> None:
    with pytest.raises(ValueError) as msg:
        RawSnapshotsDataLoader(
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
        RawSnapshotsDataLoader(
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
        RawSnapshotsDataLoader(
            resource_path=resource_path,
            asset=Asset.ADA,
            market=Market.KRAKEN_SPOT,
            since=date(year=2024, month=6, day=1),
            until=date(year=2024, month=7, day=1),
        )
    assert "Expected file" in str(msg.value) and "doesn't exist" in str(msg.value)


def test_get_data_error() -> None:
    loader = RawSnapshotsDataLoader(
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


def test_get_data_success() -> None:
    start = date(year=2024, month=6, day=25)
    end = date(year=2024, month=7, day=1)

    handler = SnapshotsDataHandler()
    loader = RawSnapshotsDataLoader(
        resource_path=resource_path,
        asset=Asset.ADA,
        market=Market.KRAKEN_SPOT,
        since=start,
        until=end,
    )

    target_path = resource_path / "snapshots" / "XADAZUSD" / "test.bin"
    targets = handler.read(target_path)
    snapshots = loader.get_data(start, end)

    assert len(snapshots) == len(targets)
    for i in range(len(snapshots)):
        assert snapshots[i].time == targets[i].time
        assert snapshots[i].bids == targets[i].bids
        assert snapshots[i].asks == targets[i].asks
        assert snapshots[i].feedcode == targets[i].feedcode
        assert snapshots[i].market == targets[i].market


def test_next_success() -> None:
    handler = SnapshotsDataHandler()
    loader = RawSnapshotsDataLoader(
        resource_path=resource_path,
        asset=Asset.ADA,
        market=Market.KRAKEN_SPOT,
        since=date(year=2024, month=6, day=25),
        until=date(year=2024, month=7, day=1),
    )

    target_path = resource_path / "snapshots" / "XADAZUSD" / "test.bin"
    targets = handler.read(target_path)

    for i in range(len(targets)):
        snapshot = loader.next()
        assert snapshot is not None
        assert snapshot.time == targets[i].time
        assert snapshot.bids == targets[i].bids
        assert snapshot.asks == targets[i].asks
        assert snapshot.feedcode == targets[i].feedcode
        assert snapshot.market == targets[i].market
    assert loader.next() is None
