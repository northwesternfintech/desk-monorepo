import pytest
from pysrc.signal.example_feature_generator import ExampleFeatureGenerator
from pysrc.adapters.messages import TradeMessage, SnapshotMessage
from pysrc.util.types import Asset, OrderSide, Market


def create_trade(
    feedcode: str,
    time: int,
    price: float,
    quantity: float,
    side: OrderSide,
    market: Market,
) -> TradeMessage:
    return TradeMessage(
        time=time,
        feedcode=feedcode,
        n_trades=1,
        price=price,
        quantity=quantity,
        side=side,
        market=market,
    )


@pytest.fixture
def generator() -> ExampleFeatureGenerator:
    return ExampleFeatureGenerator()


@pytest.fixture
def sample_trades() -> dict[str, list[TradeMessage]]:
    return {
        "BTC": [
            create_trade("BTC", 1, 100.0, 0.5, OrderSide.BID, Market.KRAKEN_SPOT),
            create_trade("BTC", 2, 105.0, 0.3, OrderSide.ASK, Market.KRAKEN_SPOT),
        ],
        "ETH": [
            create_trade("ETH", 1, 200.0, 1.0, OrderSide.BID, Market.KRAKEN_SPOT),
            create_trade("ETH", 2, 210.0, 0.8, OrderSide.ASK, Market.KRAKEN_SPOT),
            create_trade("ETH", 3, 190.0, 0.5, OrderSide.BID, Market.KRAKEN_SPOT),
        ],
    }


def test_compute_ohlc_no_trades(generator: ExampleFeatureGenerator) -> None:
    features = generator.compute_ohlc([])
    assert features == [0.0, 0.0, 0.0, 0.0]


def test_compute_ohlc_single_trade(generator: ExampleFeatureGenerator) -> None:
    trade = create_trade("BTC", 1, 100.0, 0.5, OrderSide.BID, Market.KRAKEN_SPOT)
    features = generator.compute_ohlc([trade])
    assert features == [100.0, 100.0, 100.0, 100.0]


def test_compute_ohlc_multiple_trades(generator: ExampleFeatureGenerator) -> None:
    trades = [
        create_trade("BTC", 1, 100.0, 0.5, OrderSide.BID, Market.KRAKEN_SPOT),
        create_trade("BTC", 2, 105.0, 0.3, OrderSide.ASK, Market.KRAKEN_SPOT),
        create_trade("BTC", 3, 95.0, 0.2, OrderSide.BID, Market.KRAKEN_SPOT),
        create_trade("BTC", 4, 102.0, 0.4, OrderSide.ASK, Market.KRAKEN_SPOT),
    ]
    features = generator.compute_ohlc(trades)
    assert features == [100.0, 105.0, 95.0, 102.0]


def test_on_tick(
    generator: ExampleFeatureGenerator, sample_trades: dict[str, list[TradeMessage]]
) -> None:
    snapshots: dict[str, SnapshotMessage] = {}
    output = generator.on_tick(snapshots, sample_trades)

    def assert_features(asset: Asset, expected_features: list[float]) -> None:
        assert output[asset]["features"] == expected_features

    assert_features(Asset.BTC, [100.0, 105.0, 100.0, 105.0])
    assert_features(Asset.ETH, [200.0, 210.0, 190.0, 190.0])
    assert_features(Asset.ADA, [0.0, 0.0, 0.0, 0.0])
    assert_features(Asset.SOL, [0.0, 0.0, 0.0, 0.0])
    assert_features(Asset.DOGE, [0.0, 0.0, 0.0, 0.0])

    for asset in generator.assets:
        assert len(output[asset]["features"]) == len(generator.order_features)


def test_feature_order_consistency(
    generator: ExampleFeatureGenerator, sample_trades: dict[str, list[TradeMessage]]
) -> None:
    snapshots: dict[str, SnapshotMessage] = {}
    trades = {"BTC": sample_trades["BTC"][:1]}
    output = generator.on_tick(snapshots, trades)
    features = output[Asset.BTC]["features"]
    assert features == [100.0, 100.0, 100.0, 100.0]
