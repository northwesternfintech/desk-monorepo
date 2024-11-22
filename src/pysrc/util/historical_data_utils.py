from pathlib import Path


def check_historical_data_filepath(file_path: Path, is_trade_data: bool) -> bool:
    kraken_feedcodes = [
        "XXBTZUSD",
        "XETHZUSD",
        "XWIFZUSD",
        "XXRPZUSD",
        "XSOLZUSD",
        "XDOGEZUSD",
        "XTRXZUSD",
        "XADAZUSD",
        "XAVAXZUSD",
        "XSHIBZUSD",
        "XDOTZUSD",
    ]
    if file_path.suffix != ".bin":
        return False
    if file_path.parent.name not in kraken_feedcodes:
        return False
    if is_trade_data:
        if file_path.parent.parent.name != "trades":
            return False
    else:
        if file_path.parent.parent.name != "snapshots":
            return False
    return True
