import pytest
from unittest.mock import patch
from pysrc.adapters.kraken.spot.kraken_client import KrakenClient
from pysrc.util.types import Asset
from pysrc.adapters.kraken.spot.containers import (
    SystemStatus,
    AssetInfo,
    AssetPairInfo,
    OHLCData,
    OHLCTick,
    SpreadMessage,
    AssetStatus,
)
from pysrc.adapters.messages import SnapshotMessage, TradeMessage
from pysrc.util.types import Market, OrderSide
from pysrc.util.conversions import string_to_enum

@pytest.fixture
def client():
    return KrakenClient()

@patch.object(KrakenClient, '_get')
def test_get_system_status(mock_get, client):
    mock_get.return_value = {
        "error": [],
        "result": {"status": "online", "timestamp": "2024-10-18T21:45:34Z"}
    }

    result = client.get_system_status()
    assert result == SystemStatus.ONLINE

@patch.object(KrakenClient, '_get')
def test_get_asset_info(mock_get, client):
    mock_get.return_value = {
        "error": [],
        "result": {
            "BTC": {
                "altname": "BTC",
                "aclass": "currency",
                "decimals": 8,
                "collateral_value": 1000.0,
                "status": "enabled"
            }
        }
    }

    result = client.get_asset_info(Asset.BTC)
    assert result.asset == Asset.BTC
    assert result.asset_name == "BTC"
    assert result.altname == "BTC"
    assert result.decimals == 8
    assert result.collateral_value == 1000.0
    assert result.status == AssetStatus.ENABLED

@patch.object(KrakenClient, '_get')
def test_get_order_book(mock_get, client):
    mock_get.return_value = {
        "error": [],
        "result": {
            "XXBTZUSD": {
                "bids": [["50000.0", "0.5", "1633036800"]],
                "asks": [["50500.0", "0.3", "1633036800"]]
            }
        }
    }

    result = client.get_order_book(Asset.BTC)
    assert result.feedcode == "BTCUSD"
    assert result.bids == [(50000.0, 0.5)]
    assert result.asks == [(50500.0, 0.3)]
    assert result.market == Market.KRAKEN_SPOT

@patch.object(KrakenClient, '_get')
def test_get_ohlc_data(mock_get, client):
    mock_get.return_value = {
        "error": [],
        "result": {
            "XXBTZUSD": [
                [1633036800, "48000.0", "49000.0", "47000.0", "48500.0", "48250.0", "100.0", 10]
            ],
            "last": 1633036800
        }
    }

    result = client.get_ohlc_data(Asset.BTC)
    assert result.asset == Asset.BTC
    assert result.last == 1633036800
    assert len(result.ticks) == 1
    tick = result.ticks[0]
    assert tick.time == 1633036800
    assert tick.open == "48000.0"
    assert tick.high == "49000.0"
    assert tick.low == "47000.0"
    assert tick.close == "48500.0"

@patch.object(KrakenClient, '_get')
def test_get_recent_trades(mock_get, client):
    mock_get.return_value = {
        "error": [],
        "result": {
            "XXBTZUSD": [
                ["50000.0", "0.5", "1633036800", "b", "m", "12345"]
            ]
        }
    }

    result = client.get_recent_trades(Asset.BTC)
    assert len(result) == 1
    trade = result[0]
    assert trade.price == 50000.0
    assert trade.quantity == 0.5
    assert trade.side == OrderSide.BID
    assert trade.market == Market.KRAKEN_SPOT

@patch.object(KrakenClient, '_get')
def test_get_recent_spreads(mock_get, client):
    mock_get.return_value = {
        "error": [],
        "result": {
            "XXBTZUSD": [
                ["1633036800", "50000.0", "50500.0"]
            ]
        }
    }

    result = client.get_recent_spreads(Asset.BTC)
    assert len(result) == 1
    spread = result[0]
    assert spread.time == 1633036800
    assert spread.bid == 50000.0
    assert spread.ask == 50500.0
