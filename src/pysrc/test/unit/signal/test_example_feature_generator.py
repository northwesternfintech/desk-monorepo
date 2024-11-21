import pytest
from pysrc.signal.example_feature_generator import ExampleFeatureGenerator
from pysrc.adapters.messages import TradeMessage, SnapshotMessage
from pysrc.util.types import Asset, OrderSide, Market

trades_map = {
    "BTC": [
        TradeMessage(
            time=1,
            feedcode="BTC",
            n_trades=1,
            price=100.0,
            quantity=0.5,
            side=OrderSide.BID,
            market=Market.KRAKEN_SPOT,
        ),
        TradeMessage(
            time=2,
            feedcode="BTC",
            n_trades=1,
            price=105.0,
            quantity=0.3,
            side=OrderSide.ASK,
            market=Market.KRAKEN_SPOT,
        ),
        TradeMessage(
            time=3,
            feedcode="BTC",
            n_trades=1,
            price=95.0,
            quantity=0.2,
            side=OrderSide.BID,
            market=Market.KRAKEN_SPOT,
        ),
        TradeMessage(
            time=4,
            feedcode="BTC",
            n_trades=1,
            price=102.0,
            quantity=0.4,
            side=OrderSide.ASK,
            market=Market.KRAKEN_SPOT,
        ),
    ],
    "ETH": [
        TradeMessage(
            time=1,
            feedcode="ETH",
            n_trades=1,
            price=200.0,
            quantity=1.0,
            side=OrderSide.BID,
            market=Market.KRAKEN_SPOT,
        ),
        TradeMessage(
            time=2,
            feedcode="ETH",
            n_trades=1,
            price=210.0,
            quantity=0.8,
            side=OrderSide.ASK,
            market=Market.KRAKEN_SPOT,
        ),
        TradeMessage(
            time=3,
            feedcode="ETH",
            n_trades=1,
            price=190.0,
            quantity=0.5,
            side=OrderSide.BID,
            market=Market.KRAKEN_SPOT,
        ),
    ],
}


def test_compute_ohlc_no_trades() -> None:
    generator = ExampleFeatureGenerator()
    features = generator.compute_ohlc([])
    assert features == [0.0, 0.0, 0.0, 0.0]


def test_compute_ohlc_single_trade() -> None:
    generator = ExampleFeatureGenerator()
    features = generator.compute_ohlc([trades_map["BTC"][0]])
    assert features == [100.0, 100.0, 100.0, 100.0]


def test_compute_ohlc_multiple_trades() -> None:
    generator = ExampleFeatureGenerator()
    features = generator.compute_ohlc(trades_map["BTC"])
    expected_features = [100.0, 105.0, 95.0, 102.0]
    assert features == expected_features


def test_on_tick() -> None:
    generator = ExampleFeatureGenerator()
    trades = {
        "BTC": trades_map["BTC"][:2],
        "ETH": trades_map["ETH"],
    }
    snapshots: dict[str, SnapshotMessage] = {}
    output = generator.on_tick(snapshots, trades)

    assert output[Asset.BTC]["features"] == [100.0, 105.0, 100.0, 105.0]
    assert output[Asset.ETH]["features"] == [200.0, 210.0, 190.0, 190.0]

    assert output[Asset.ADA]["features"] == [0.0, 0.0, 0.0, 0.0]
    assert output[Asset.SOL]["features"] == [0.0, 0.0, 0.0, 0.0]
    assert output[Asset.DOGE]["features"] == [0.0, 0.0, 0.0, 0.0]

    for asset in generator.assets:
        assert len(output[asset]["features"]) == len(generator.order_features)


def test_feature_order_consistency() -> None:
    generator = ExampleFeatureGenerator()
    trades = {
        "BTC": [trades_map["BTC"][0]],
    }
    snapshots: dict[str, SnapshotMessage] = {}
    output = generator.on_tick(snapshots, trades)
    features = output[Asset.BTC]["features"]
    assert features == [100.0, 100.0, 100.0, 100.0]
