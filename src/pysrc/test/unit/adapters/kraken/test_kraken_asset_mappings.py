import pytest

from pysrc.adapters.kraken.asset_mappings import asset_to_kraken, kraken_to_asset, kraken_to_market
from pysrc.util.types import Asset, Market


def test_asset_conversion() -> None:
    for asset in Asset:
        assert kraken_to_asset(asset_to_kraken(asset, Market.KRAKEN_SPOT)) == asset
        assert kraken_to_asset(asset_to_kraken(asset, Market.KRAKEN_USD_FUTURE)) == asset

        assert kraken_to_market(asset_to_kraken(asset, Market.KRAKEN_SPOT)) == Market.KRAKEN_SPOT
        assert kraken_to_market(asset_to_kraken(asset, Market.KRAKEN_USD_FUTURE)) == Market.KRAKEN_USD_FUTURE

    with pytest.raises(Exception):
        kraken_to_asset("BONKUSD")

    with pytest.raises(Exception):
        kraken_to_market("BONKUSD")
