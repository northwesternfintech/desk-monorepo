from pysrc.util.instrument import Instrument
from pysrc.util.types import Market, Asset
from pathlib import Path


def get_test_instrument() -> Instrument:
    return Instrument(Market.KRAKEN_SPOT, Asset.BTC)


def get_resources_path(file_location: str) -> Path:
    return Path(file_location).parent.joinpath("resources")
