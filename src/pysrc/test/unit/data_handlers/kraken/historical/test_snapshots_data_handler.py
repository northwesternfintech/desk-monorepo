import pytest
import numpy as np
import os
import random
from datetime import date

from pysrc.test.helpers import get_resources_path
from pysrc.data_handlers.kraken.historical.snapshots_data_handler import (
    SnapshotsDataHandler,
)
from pysrc.adapters.messages import SnapshotMessage
from pysrc.util.types import Market

random.seed(42)
resource_path = get_resources_path(__file__)


def test_read_write_to_file() -> None:
    handler = SnapshotsDataHandler(resource_path / "trades")

    snapshots = [
        SnapshotMessage(
            time=1,
            feedcode="BONKUSD",
            market=Market.KRAKEN_USD_FUTURE,
            bids=[],
            asks=[[1.0, 2.0]],
        ),
        SnapshotMessage(
            time=2,
            feedcode="BONKUSD",
            market=Market.KRAKEN_USD_FUTURE,
            bids=[[3.0, 4.0], [5.0, -6.0], [68717.5, -3000.0]],
            asks=[[1.0, 2.0], [68717.5, -3000.0]],
        ),
        SnapshotMessage(
            time=10,
            feedcode="BONKUSD",
            market=Market.KRAKEN_USD_FUTURE,
            bids=[[3.0, 4.0], [5.0, -6.0], [68717.5, -3000.0], [7.0, -8.0]],
            asks=[[1.0, 2.0], [68717.5, -3000.0]],
        ),
    ]

    test_file_path = resource_path / "snapshots" / "BONKUSD" / "test.bin"
    handler.write_to_file(test_file_path, snapshots)
    restored_snapshots = handler.read_file(test_file_path)

    assert len(snapshots) == len(restored_snapshots)
    for i in range(len(snapshots)):
        assert snapshots[i].feedcode == restored_snapshots[i].feedcode
        assert snapshots[i].market == restored_snapshots[i].market
        assert snapshots[i].time == restored_snapshots[i].time
        assert snapshots[i].bids == restored_snapshots[i].bids
        assert snapshots[i].asks == restored_snapshots[i].asks


def test_stream_data() -> None:
    handler = SnapshotsDataHandler(resource_path / "snapshots")

    snapshots = []
    for i in range(9):
        snapshots.append(
            SnapshotMessage(
                time=i,
                feedcode="AEVOEUR",
                market=Market.KRAKEN_USD_FUTURE,
                bids=[
                    [random.uniform(0, 100), random.uniform(0, 10)]
                    for _ in range(i + 1)
                ],
                asks=[
                    [random.uniform(0, 100), random.uniform(0, 10)]
                    for _ in range(i + 2)
                ],
            )
        )

    test_file_paths = [
        resource_path / "snapshots" / "AEVOEUR" / "11_11_2024.bin",
        resource_path / "snapshots" / "AEVOEUR" / "11_12_2024.bin",
        resource_path / "snapshots" / "AEVOEUR" / "11_13_2024.bin",
        resource_path / "snapshots" / "AEVOEUR" / "11_14_2024.bin",
        resource_path / "snapshots" / "AEVOEUR" / "11_15_2024.bin",
    ]

    handler.write_to_file(test_file_paths[0], snapshots[:3])
    handler.write_to_file(test_file_paths[1], snapshots[3:5])
    handler.write_to_file(test_file_paths[2], snapshots[5:6])
    handler.write_to_file(test_file_paths[3], [])
    handler.write_to_file(test_file_paths[4], snapshots[6:])

    gen = handler.stream_data(
        "AEVOEUR",
        date(year=2024, month=11, day=11),
        date(year=2024, month=11, day=16),
    )

    for i in range(len(snapshots)):
        snapshot = next(gen)
        assert snapshot.feedcode == snapshots[i].feedcode
        assert snapshot.market == snapshots[i].market
        assert snapshot.time == snapshots[i].time
        assert snapshot.bids == snapshots[i].bids
        assert snapshot.asks == snapshots[i].asks

    with pytest.raises(StopIteration):
        next(gen)