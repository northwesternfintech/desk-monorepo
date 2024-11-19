import pytest
from unittest.mock import MagicMock, patch
import time
import numpy as np

from pysrc.util.types import Asset
from pysrc.adapters.kraken.spot.kraken_client import KrakenClient
from pysrc.adapters.messages import SnapshotMessage
from pysrc.targets.log_return import TargetLogReturn
from pysrc.util.types import Market


@pytest.fixture
def asset() -> Asset:
    return Asset.BTC


@pytest.fixture
def snapshot() -> SnapshotMessage:
    return SnapshotMessage(
        bids=[[10000.0, 1.0]],
        asks=[[10010.0, 1.0]],
        time=int(time.time()),
        feedcode="BTCUSD",
        market=Market.KRAKEN_SPOT,
    )


@pytest.fixture
def kraken_client_mock(snapshot: SnapshotMessage) -> KrakenClient:
    client = MagicMock(spec=KrakenClient)
    client.get_order_book.return_value = snapshot
    return client


def test_initialization(
    asset: Asset, snapshot: SnapshotMessage, kraken_client_mock: KrakenClient
) -> None:
    with patch(
        "pysrc.targets.log_return.KrakenClient", return_value=kraken_client_mock
    ):
        target = TargetLogReturn(time_delay=1, asset=asset)
        assert len(target._buffer) == 1
        assert target._buffer[0] == snapshot


def test_update(asset: Asset, kraken_client_mock: KrakenClient) -> None:
    with patch(
        "pysrc.targets.log_return.KrakenClient", return_value=kraken_client_mock
    ):
        target = TargetLogReturn(time_delay=1, asset=asset)
        new_snapshot = SnapshotMessage(
            bids=[[10000.0, 1.0]],
            asks=[[10010.0, 1.0]],
            time=int(time.time()),
            feedcode="BTCUSD",
            market=Market.KRAKEN_SPOT,
        )
        target.update(new_snapshot)
        assert target._buffer[-1] == new_snapshot


def test_compute_midprice(snapshot: SnapshotMessage) -> None:
    target = TargetLogReturn(time_delay=1, asset=Asset.BTC)
    midprice = target.compute_midprice(snapshot)
    assert midprice == 10005


def test_next(asset: Asset, kraken_client_mock: KrakenClient) -> None:
    with patch(
        "pysrc.targets.log_return.KrakenClient", return_value=kraken_client_mock
    ):
        target = TargetLogReturn(time_delay=1, asset=asset)
        log_return = target.next()
        assert isinstance(log_return, float)
        assert log_return == 0.0


def test_complicated_next(asset: Asset, kraken_client_mock: KrakenClient) -> None:
    with patch(
        "pysrc.targets.log_return.KrakenClient", return_value=kraken_client_mock
    ):
        target = TargetLogReturn(time_delay=50, asset=asset)
        initial_snapshot = SnapshotMessage(
            bids=[[10050.0, 1.0]],
            asks=[[10100.0, 1.0]],
            time=int(time.time()),
            feedcode="BTCUSD",
            market=Market.KRAKEN_SPOT,
        )
        target.update(initial_snapshot)

        for _ in range(48):
            target.update(initial_snapshot)

        log_return = target.next()
        expected_log_return = np.log(10005.0 / 10075.0)

        assert isinstance(log_return, float)
        assert np.isclose(log_return, expected_log_return)
