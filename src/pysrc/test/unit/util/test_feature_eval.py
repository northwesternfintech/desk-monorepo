import os
from datetime import datetime

import pytest
from pyzstd import CParameter, compress

from pysrc.adapters.messages import SnapshotMessage, TradeMessage
from pysrc.signal.base_feature_generator import BaseFeatureGenerator
from pysrc.test.feature_eval_helpers import TestFeatureGenerator
from pysrc.test.helpers import get_resources_path
from pysrc.util.feature_eval import Evaluator
from pysrc.util.types import Market, OrderSide

resource_path = str(get_resources_path(__file__))


@pytest.fixture
def client() -> Evaluator:
    test_features = ["a", "b", "c"]
    asset = "XXBTZUSD"
    start = datetime(year=2024, month=11, day=22)
    end = datetime(year=2024, month=11, day=22)
    return Evaluator(features=test_features, asset=asset, start=start, end=end)


@pytest.fixture
def feature_gen() -> BaseFeatureGenerator:
    return TestFeatureGenerator()


# Test feature calculation
def test_feature_calculation(
    client: Evaluator, feature_gen: BaseFeatureGenerator
) -> None:
    snapshots = [
        SnapshotMessage(
            time=1,
            feedcode="XXBTZUSD",
            market=Market.KRAKEN_USD_FUTURE,
            bids=[],
            asks=[[1.0, 2.0]],
        ),
        SnapshotMessage(
            time=2,
            feedcode="XXBTZUSD",
            market=Market.KRAKEN_USD_FUTURE,
            bids=[[3.0, 4.0], [68717.5, -3000.0]],
            asks=[[1.0, 2.0], [68717.5, -3000.0]],
        ),
        SnapshotMessage(
            time=3,
            feedcode="XXBTZUSD",
            market=Market.KRAKEN_USD_FUTURE,
            bids=[[3.0, 4.0], [68717.5, -3000.0], [7.0, 8.0]],
            asks=[[1.0, 2.0], [68717.5, -3000.0]],
        ),
    ]

    snapshots_bytes = b""
    for s in snapshots:
        snapshots_bytes += s.to_bytes()

    test_dir_snapshots = os.path.join(resource_path, "snapshots/XXBTZUSD")
    os.makedirs(test_dir_snapshots, exist_ok=True)
    test_path = os.path.join(test_dir_snapshots, "11_22_2024.bin")
    with open(test_path, "wb") as f:
        f.write(
            compress(snapshots_bytes, level_or_option={CParameter.compressionLevel: 10})
        )

    trades = [
        TradeMessage(
            1, "XXBTZUSD", 1, 10.0, 1.0, OrderSide.BID, Market.KRAKEN_USD_FUTURE
        ),
        TradeMessage(
            2, "XXBTZUSD", 1, 10.02, 0.5, OrderSide.BID, Market.KRAKEN_USD_FUTURE
        ),
        TradeMessage(
            3, "XXBTZUSD", 1, 9.99, 1.5, OrderSide.BID, Market.KRAKEN_USD_FUTURE
        ),
    ]

    trades_bytes = b""
    for t in trades:
        trades_bytes += t.to_bytes()

    test_dir_trades = os.path.join(resource_path, "trades/XXBTZUSD")
    os.makedirs(test_dir_trades, exist_ok=True)
    test_path = os.path.join(test_dir_trades, "11_22_2024.bin")
    with open(test_path, "wb") as f:
        f.write(
            compress(trades_bytes, level_or_option={CParameter.compressionLevel: 10})
        )

    trade_resource = os.path.join(resource_path, "trades")
    snapshot_resource = os.path.join(resource_path, "snapshots")
    result = client.calculate_features(feature_gen, trade_resource, snapshot_resource)
    assert result["a"] == [7.0, 7.0, 7.0]
    assert result["b"] == [7.0, 7.0, 7.0]
    assert result["c"] == [7.0, 7.0, 7.0]


# Test feature evaluation
def test_feature_evaluation(client: Evaluator) -> None:
    features = {"a": [1.0, 2.0, 3.0], "b": [2.0, 4.0, 6.0], "c": [3.0, 6.0, 9.0]}

    target = [4.0, 8.0, 12.0]
    result = client.evaluate_features(features, target)

    assert result is not None
