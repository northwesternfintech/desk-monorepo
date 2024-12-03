import os
from datetime import datetime

import pytest
from pyzstd import CParameter, compress

from pysrc.adapters.messages import SnapshotMessage, TradeMessage
from pysrc.signal.base_feature_generator import BaseFeatureGenerator
from pysrc.signal.example_kraken_feature_generator import ExampleKrakenFeatureGenerator
from pysrc.test.helpers import get_resources_path
from pysrc.util.feature_eval import Evaluator
from pysrc.util.types import Asset, Market, OrderSide

resource_path = get_resources_path(__file__)


@pytest.fixture
def client() -> Evaluator:
    test_features = ["open", "high", "low", "close"]
    asset = Asset.BTC
    market = Market.KRAKEN_SPOT
    start = datetime(year=2024, month=6, day=25)
    end = datetime(year=2024, month=6, day=26)
    return Evaluator(
        features=test_features,
        asset=asset,
        market=market,
        start=start,
        end=end,
        resource_path=resource_path,
    )


@pytest.fixture
def feature_gen() -> BaseFeatureGenerator:
    return ExampleKrakenFeatureGenerator()


def test_feature_calculation(
    client: Evaluator, feature_gen: BaseFeatureGenerator
) -> None:
    snapshots = [
        SnapshotMessage(
            time=1719273600,
            feedcode="XXBTZUSD",
            market=Market.KRAKEN_SPOT,
            bids=[],
            asks=[[1.0, 2.0]],
        ),
        SnapshotMessage(
            time=1719273600,
            feedcode="XXBTZUSD",
            market=Market.KRAKEN_SPOT,
            bids=[[3.0, 4.0], [68717.5, -3000.0]],
            asks=[[1.0, 2.0], [68717.5, -3000.0]],
        ),
        SnapshotMessage(
            time=1719273601,
            feedcode="XXBTZUSD",
            market=Market.KRAKEN_SPOT,
            bids=[[3.0, 4.0], [68717.5, -3000.0], [7.0, 8.0]],
            asks=[[1.0, 2.0], [68717.5, -3000.0]],
        ),
        SnapshotMessage(
            time=1719273602,
            feedcode="XXBTZUSD",
            market=Market.KRAKEN_SPOT,
            bids=[[3.0, 4.0], [68717.5, -3000.0], [7.0, 8.0]],
            asks=[[1.0, 2.0], [68717.5, -3000.0]],
        ),
    ]

    snapshots_bytes = b""
    for s in snapshots:
        snapshots_bytes += s.to_bytes()

    test_dir_snapshots = resource_path / "snapshots" / "XXBTZUSD"
    os.makedirs(test_dir_snapshots, exist_ok=True)
    test_path = test_dir_snapshots / "06_25_2024.bin"

    with open(test_path, "wb") as f:
        f.write(
            compress(snapshots_bytes, level_or_option={CParameter.compressionLevel: 10})
        )

    trades = [
        TradeMessage(
            1719273600, "XXBTZUSD", 1, 10.0, 1.0, OrderSide.BID, Market.KRAKEN_SPOT
        ),
        TradeMessage(
            1719273600, "XXBTZUSD", 1, 10.02, 0.5, OrderSide.BID, Market.KRAKEN_SPOT
        ),
        TradeMessage(
            1719273601, "XXBTZUSD", 1, 9.9, 1.5, OrderSide.BID, Market.KRAKEN_SPOT
        ),
        TradeMessage(
            1719273602, "XXBTZUSD", 1, 9.0, 1.5, OrderSide.BID, Market.KRAKEN_SPOT
        ),
    ]

    trades_bytes = b""
    for t in trades:
        trades_bytes += t.to_bytes()

    test_dir_snapshots = resource_path / "trades" / "XXBTZUSD"
    os.makedirs(test_dir_snapshots, exist_ok=True)
    test_path = test_dir_snapshots / "06_25_2024.bin"

    with open(test_path, "wb") as f:
        f.write(
            compress(trades_bytes, level_or_option={CParameter.compressionLevel: 10})
        )

    result = client.calculate_features(feature_gen)
    assert result["open"][0] == pytest.approx(10.0, rel=1e-7)
    assert result["open"][1] == pytest.approx(9.9, rel=1e-7)
    assert result["open"][2] == pytest.approx(9.0, rel=1e-7)

    assert result["high"][0] == pytest.approx(10.02, rel=1e-7)
    assert result["high"][1] == pytest.approx(9.9, rel=1e-7)
    assert result["high"][2] == pytest.approx(9.0, rel=1e-7)

    assert result["low"][0] == pytest.approx(10.0, rel=1e-7)
    assert result["low"][1] == pytest.approx(9.9, rel=1e-7)
    assert result["low"][2] == pytest.approx(9.0, rel=1e-7)

    assert result["close"][0] == pytest.approx(10.02, rel=1e-7)
    assert result["close"][1] == pytest.approx(9.9, rel=1e-7)
    assert result["close"][2] == pytest.approx(9.0, rel=1e-7)


def test_feature_evaluation(client: Evaluator) -> None:
    features = {
        "open": [1.0, 2.0, 3.0],
        "high": [2.0, 4.0, 6.0],
        "low": [-1.0, -2.0, -3.0],
        "close": [1.0, 2.0, 3.0],
    }

    target = [4.0, 8.0, 12.0]
    result = client.evaluate_features(features, target)

    assert result is not None

    expected_result = [
        [1, 1, -1, 1, 1],
        [1, 1, -1, 1, 1],
        [-1, -1, 1, -1, -1],
        [1, 1, -1, 1, 1],
        [1, 1, -1, 1, 1],
    ]

    assert (result == expected_result).any()
