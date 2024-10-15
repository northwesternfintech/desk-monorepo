from pysrc.util.instrument import Instrument
from pysrc.util.types import Market, Asset


def get_test_instrument() -> Instrument:
    return Instrument(Market.KRAKEN_SPOT, Asset.BTC)
