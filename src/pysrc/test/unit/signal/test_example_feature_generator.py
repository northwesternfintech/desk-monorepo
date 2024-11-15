import pytest
from pysrc.adapters.messages import TradeMessage
from pysrc.util.types import Asset, OrderSide, Market
from pysrc.signal.example_feature_generator import OHLCFeatureGenerator


@pytest.fixture
def generator():
    return OHLCFeatureGenerator()


def test_ohlc_with_single_trade(generator):
    trade = TradeMessage(
        time=1234567890,
        price=100.0,
        quantity=10,
        feedcode="BTC/USD",
        n_trades=1,
        side=OrderSide.BID,
        market=Market.KRAKEN_SPOT,
    )
    trades = {Asset.BTC: [trade]}
    result = generator.on_tick({}, trades)

    expected = {
        Asset.BTC: {
            "open": [100.0],
            "high": [100.0],
            "low": [100.0],
            "close": [100.0],
        }
    }
    assert result == expected


def test_ohlc_with_multiple_trades(generator):
    trades = {
        Asset.BTC: [
            TradeMessage(
                time=1234567890,
                price=100.0,
                quantity=10,
                feedcode="BTC/USD",
                n_trades=1,
                side=OrderSide.BID,
                market=Market.KRAKEN_SPOT,
            ),
            TradeMessage(
                time=1234567891,
                price=105.0,
                quantity=5,
                feedcode="BTC/USD",
                n_trades=1,
                side=OrderSide.BID,
                market=Market.KRAKEN_SPOT,
            ),
            TradeMessage(
                time=1234567892,
                price=95.0,
                quantity=8,
                feedcode="BTC/USD",
                n_trades=1,
                side=OrderSide.BID,
                market=Market.KRAKEN_SPOT,
            ),
            TradeMessage(
                time=1234567893,
                price=102.0,
                quantity=7,
                feedcode="BTC/USD",
                n_trades=1,
                side=OrderSide.BID,
                market=Market.KRAKEN_SPOT,
            ),
        ]
    }
    result = generator.on_tick({}, trades)

    expected = {
        Asset.BTC: {
            "open": [100.0],
            "high": [105.0],
            "low": [95.0],
            "close": [102.0],
        }
    }
    assert result == expected


def test_ohlc_with_empty_trades(generator):
    trades = {Asset.BTC: []}
    result = generator.on_tick({}, trades)

    expected = {
        Asset.BTC: {
            "open": [None],
            "high": [None],
            "low": [None],
            "close": [None],
        }
    }
    assert result == expected


def test_ohlc_with_multiple_assets(generator):
    trades = {
        Asset.BTC: [
            TradeMessage(
                time=1234567890,
                price=100.0,
                quantity=10,
                feedcode="BTC/USD",
                n_trades=1,
                side=OrderSide.BID,
                market=Market.KRAKEN_SPOT,
            ),
            TradeMessage(
                time=1234567891,
                price=105.0,
                quantity=5,
                feedcode="BTC/USD",
                n_trades=1,
                side=OrderSide.BID,
                market=Market.KRAKEN_SPOT,
            ),
        ],
        Asset.ETH: [
            TradeMessage(
                time=1234567892,
                price=200.0,
                quantity=10,
                feedcode="ETH/USD",
                n_trades=1,
                side=OrderSide.BID,
                market=Market.KRAKEN_SPOT,
            ),
            TradeMessage(
                time=1234567893,
                price=195.0,
                quantity=8,
                feedcode="ETH/USD",
                n_trades=1,
                side=OrderSide.BID,
                market=Market.KRAKEN_SPOT,
            ),
            TradeMessage(
                time=1234567894,
                price=210.0,
                quantity=5,
                feedcode="ETH/USD",
                n_trades=1,
                side=OrderSide.BID,
                market=Market.KRAKEN_SPOT,
            ),
        ],
    }
    result = generator.on_tick({}, trades)

    expected = {
        Asset.BTC: {
            "open": [100.0],
            "high": [105.0],
            "low": [100.0],
            "close": [105.0],
        },
        Asset.ETH: {
            "open": [200.0],
            "high": [210.0],
            "low": [195.0],
            "close": [210.0],
        },
    }
    assert result == expected
