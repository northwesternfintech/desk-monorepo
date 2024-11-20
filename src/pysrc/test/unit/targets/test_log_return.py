import pytest
import time
import numpy as np
from unittest.mock import MagicMock, patch

from pysrc.util.types import Asset, Market
from pysrc.adapters.messages import SnapshotMessage
from pysrc.targets.log_return import TargetLogReturn

mock_snapshot = SnapshotMessage(
    bids=[[10000.0, 1.0]],
    asks=[[10010.0, 1.0]],
    time=int(time.time()),
    feedcode="BTCUSD",
    market=Market.KRAKEN_SPOT,
)

asset = Asset.BTC


@patch("pysrc.targets.log_return.KrakenClient")
def test_initialization(mock_kraken_client: MagicMock) -> None:
    mock_kraken_client.return_value.get_order_book.return_value = mock_snapshot

    target = TargetLogReturn(time_delay=1, asset=asset)

    assert len(target._buffer) == 1
    assert target._buffer[0].bids == mock_snapshot.bids
    assert target._buffer[0].asks == mock_snapshot.asks


@patch("pysrc.targets.log_return.KrakenClient")
def test_update(mock_kraken_client: MagicMock) -> None:
    mock_kraken_client.return_value.get_order_book.return_value = mock_snapshot

    target = TargetLogReturn(time_delay=1, asset=asset)
    target.update(mock_snapshot)

    assert target._buffer[-1] == mock_snapshot


@patch("pysrc.targets.log_return.KrakenClient")
def test_compute_midprice(mock_kraken_client: MagicMock) -> None:
    mock_kraken_client.return_value.get_order_book.return_value = mock_snapshot

    target = TargetLogReturn(time_delay=1, asset=Asset.BTC)

    midprice = target.compute_midprice(mock_snapshot)

    assert np.isclose(midprice, 10005.0)


@patch("pysrc.targets.log_return.KrakenClient")
def test_next(mock_kraken_client: MagicMock) -> None:
    mock_kraken_client.return_value.get_order_book.return_value = mock_snapshot

    target = TargetLogReturn(time_delay=1, asset=asset)
    log_return = target.next()

    assert isinstance(log_return, float)
    assert log_return == 0.0


@patch("pysrc.targets.log_return.KrakenClient")
def test_complicated_next(mock_kraken_client: MagicMock) -> None:
    mock_kraken_client.return_value.get_order_book.return_value = mock_snapshot

    target = TargetLogReturn(time_delay=50, asset=asset)

    snapshot = SnapshotMessage(
        bids=[[10050.0, 1.0]],
        asks=[[10100.0, 1.0]],
        time=int(time.time()),
        feedcode="BTCUSD",
        market=Market.KRAKEN_SPOT,
    )

    for _ in range(49):
        target.update(snapshot)

    log_return = target.next()
    expected_log_return = np.log(10005.0 / 10075.0)

    assert isinstance(log_return, float)
    assert np.isclose(log_return, expected_log_return)


@patch("pysrc.targets.log_return.KrakenClient")
def test_random_next(mock_kraken_client: MagicMock) -> None:
    mock_kraken_client.return_value.get_order_book.return_value = mock_snapshot

    target = TargetLogReturn(time_delay=10, asset=asset)
    snapshots = []

    for _ in range(10):
        snapshot = SnapshotMessage(
            bids=[[10000.0 + 10 * np.random.rand(), 1.0]],
            asks=[[10010.0 + 10 * np.random.rand(), 1.0]],
            time=int(time.time()),
            feedcode="BTCUSD",
            market=Market.KRAKEN_SPOT,
        )
        snapshots.append(snapshot)
        target.update(snapshot)

    log_return = target.next()
    expected_left_midprice = target.compute_midprice(snapshots[1])
    expected_right_midprice = 10005.0
    expected_log_return = np.log(expected_right_midprice / expected_left_midprice)

    assert isinstance(log_return, float)
    assert np.isclose(log_return, expected_log_return)
