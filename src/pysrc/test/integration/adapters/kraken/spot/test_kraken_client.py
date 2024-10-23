import pytest
from pysrc.adapters.kraken.spot.kraken_client import KrakenClient
from enum import Enum
from pysrc.util.types import Asset
from pysrc.adapters.kraken.spot.containers import (
    SystemStatus,
    AssetInfo,
    AssetPairInfo,
    OHLCData,
    AssetStatus,
    OHLCTick,
)


def test_system_status() -> None:
    client = KrakenClient()
    assert client.get_system_status() == SystemStatus.ONLINE


def test_get_asset_info() -> None:
    client = KrakenClient()
    res = client.get_asset_info(Asset.BTC)
    assert res.asset_name == "XBT" and res.status == AssetStatus.ENABLED


def test_get_tradeable_asset_pairs() -> None:
    client = KrakenClient()

    res = client.get_tradeable_asset_pairs([Asset.BTC])
    assert "BTC/USDT" in res


def test_get_ohlc_data() -> None:
    client = KrakenClient()
    res = client.get_ohlc_data(Asset.BTC)
    assert res.asset == Asset.BTC


def test_get_order_book() -> None:
    client = KrakenClient()
    res = client.get_order_book(Asset.BTC)
    assert res.feedcode == "BTCUSD"


def test_get_recent_trades() -> None:
    client = KrakenClient()
    res = client.get_recent_trades(Asset.BTC)
    assert res[0].feedcode == "BTCUSD"


def test_get_recent_spreads() -> None:
    client = KrakenClient()
    res = client.get_recent_spreads(Asset.BTC)
    assert res[0].feedcode == "BTCUSD"
