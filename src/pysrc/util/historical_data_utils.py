from pathlib import Path

from pysrc.adapters.kraken.asset_mappings import kraken_to_market


def check_historical_data_filepath(file_path: Path, is_trade_data: bool) -> bool:
    if file_path.suffix != ".bin":
        return False

    try:
        kraken_to_market(file_path.parent.name)
    except Exception as _:
        return False

    if is_trade_data:
        if file_path.parent.parent.name != "trades":
            return False
    else:
        if file_path.parent.parent.name != "snapshots":
            return False
    return True
