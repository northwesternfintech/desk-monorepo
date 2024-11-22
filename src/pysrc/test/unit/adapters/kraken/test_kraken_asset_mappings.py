import pytest

from pysrc.adapters.kraken.asset_mappings import asset_to_kraken, kraken_to_asset
from pysrc.util.types import Asset


def test_asset_conversion() -> None:
    for asset in Asset:
        assert kraken_to_asset(asset_to_kraken(asset)) == asset
