from datetime import date
from pathlib import Path

import numpy as np
import pytest

from pysrc.data_loaders.tick_trades_data_loader import TickTradesDataLoader
from pysrc.util.types import Asset, Market

resource_path = Path(__file__).parent / "resources"


def test_initialization_error() -> None:
    with pytest.raises(AssertionError) as msg:
        TickTradesDataLoader(
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

    with pytest.raises(AssertionError) as msg:
        TickTradesDataLoader(
            resource_path=resource_path / "lol",
            asset=Asset.ADA,
            market=Market.KRAKEN_SPOT,
            since=date(year=2024, month=6, day=25),
            until=date(year=2024, month=7, day=1),
        )
    assert "Directory for asset trades data" in str(
        msg.value
    ) and "doesn't exist" in str(msg.value)

    with pytest.raises(AssertionError) as msg:
        TickTradesDataLoader(
            resource_path=resource_path,
            asset=Asset.ADA,
            market=Market.KRAKEN_SPOT,
            since=date(year=2024, month=6, day=1),
            until=date(year=2024, month=7, day=1),
        )
    assert "Expected file" in str(msg.value) and "doesn't exist" in str(msg.value)


def test_get_data_error() -> None:
    loader = TickTradesDataLoader(
        resource_path=resource_path,
        asset=Asset.ADA,
        market=Market.KRAKEN_SPOT,
        since=date(year=2024, month=6, day=25),
        until=date(year=2024, month=7, day=1),
    )

    with pytest.raises(AssertionError) as msg:
        loader.get_data(
            since=date(year=2024, month=6, day=1),
            until=date(year=2024, month=7, day=1),
        )
    assert "Expected file" in str(msg.value) and "doesn't exist" in str(msg.value)

    with pytest.raises(AssertionError) as msg:
        loader.get_data(
            since=date(year=2024, month=6, day=25),
            until=date(year=2024, month=7, day=2),
        )
    assert "Expected file" in str(msg.value) and "doesn't exist" in str(msg.value)


def test_get_data_and_next_success() -> None:
    start = date(year=2024, month=6, day=26)
    end = date(year=2024, month=6, day=30)
    loader = TickTradesDataLoader(
        resource_path=resource_path,
        asset=Asset.ADA,
        market=Market.KRAKEN_SPOT,
        since=start,
        until=end,
    )

    targets = np.loadtxt(
        resource_path / "trades" / "XADAZUSD" / "test.csv",
        delimiter=",",
        dtype=[("time", "u8"), ("price", "f4"), ("volume", "f4")],
    )
    mask = (targets["time"] >= loader._date_to_timestamp(start)) & (
        targets["time"] <= loader._date_to_timestamp(end)
    )
    targets = targets[mask]
    all_trades = loader.get_data(start, end)

    target_idx = 0
    all_trades_idx = 0
    count = 0
    cur_epoch = loader._date_to_timestamp(start)
    while True:
        tick_trades = loader.next()
        if tick_trades is None:
            break

        assert len(tick_trades) == len(all_trades[all_trades_idx])
        for i in range(len(tick_trades)):
            assert tick_trades[i].time == cur_epoch
            assert tick_trades[i].time == targets[target_idx][0]
            assert tick_trades[i].price == targets[target_idx][1]
            assert tick_trades[i].quantity == targets[target_idx][2]

            assert tick_trades[i].time == all_trades[all_trades_idx][i].time
            assert tick_trades[i].price == all_trades[all_trades_idx][i].price
            assert tick_trades[i].quantity == all_trades[all_trades_idx][i].quantity
            target_idx += 1

        all_trades_idx += 1
        cur_epoch += 1
        count += 1

    assert count == 60 * 60 * 24 * 4
    assert len(all_trades) == 60 * 60 * 24 * 4
