import pytest
from pysrc.adapters.messages import TradeMessage
from pysrc.util.types import OrderSide, Market
from pysrc.signal.example_feature_generator import OHLCFeatureGenerator


@pytest.fixture
def generator() -> OHLCFeatureGenerator:
    return OHLCFeatureGenerator()


def test_ohlc_with_single_trade(generator: OHLCFeatureGenerator) -> None:
    trade = TradeMessage(
        time=1234567890,
        price=100.0,
        quantity=10,
        feedcode="BTC/USD",
        n_trades=1,
        side=OrderSide.BID,
        market=Market.KRAKEN_SPOT,
    )
    trades: dict[str, TradeMessage] = {"BTC/USD": trade}
    result = generator.on_tick({}, trades)

    expected = {
        "BTC/USD": {
            "open": [100.0],
            "high": [100.0],
            "low": [100.0],
            "close": [100.0],
        }
    }
    assert result == expected


def test_ohlc_with_multiple_trades(generator: OHLCFeatureGenerator) -> None:
    trades: dict[str, TradeMessage] = {
        "BTC/USD": TradeMessage(
            time=1234567890,
            price=100.0,
            quantity=10,
            feedcode="BTC/USD",
            n_trades=1,
            side=OrderSide.BID,
            market=Market.KRAKEN_SPOT,
        )
    }
    result = generator.on_tick({}, trades)

    expected = {
        "BTC/USD": {
            "open": [100.0],
            "high": [105.0],
            "low": [95.0],
            "close": [102.0],
        }
    }
    assert result == expected


def test_ohlc_with_empty_trades(generator: OHLCFeatureGenerator) -> None:
    trades: dict[str, TradeMessage] = {}
    result = generator.on_tick({}, trades)

    expected = {}
    assert result == expected


def test_ohlc_with_multiple_assets(generator: OHLCFeatureGenerator) -> None:
    trades: dict[str, TradeMessage] = {
        "BTC/USD": TradeMessage(
            time=1234567890,
            price=100.0,
            quantity=10,
            feedcode="BTC/USD",
            n_trades=1,
            side=OrderSide.BID,
            market=Market.KRAKEN_SPOT,
        ),
        "ETH/USD": TradeMessage(
            time=1234567892,
            price=200.0,
            quantity=10,
            feedcode="ETH/USD",
            n_trades=1,
            side=OrderSide.BID,
            market=Market.KRAKEN_SPOT,
        ),
    }
    result = generator.on_tick({}, trades)

    expected = {
        "BTC/USD": {
            "open": [100.0],
            "high": [100.0],
            "low": [100.0],
            "close": [100.0],
        },
        "ETH/USD": {
            "open": [200.0],
            "high": [200.0],
            "low": [200.0],
            "close": [200.0],
        },
    }
    assert result == expected
