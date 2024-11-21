import pytest
from pathlib import Path
from pysrc.util.historical_data_utils import check_historical_data_filepath


def test_valid_historical_data_filepath() -> None:
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

    for feedcode in kraken_feedcodes:
        trades_path = Path(__file__).parent / "trades" / feedcode / "data.bin"
        snapshots_path = Path(__file__).parent / "snapshots" / feedcode / "data.bin"
        assert check_historical_data_filepath(trades_path, True)
        assert check_historical_data_filepath(snapshots_path, False)


def test_invalid_historical_data_filepath() -> None:
    invalid_path_not_file = Path(__file__).parent / "trades" / "XXBTZUSD"
    assert not check_historical_data_filepath(invalid_path_not_file, True)

    invalid_path_not_binary_file = (
        Path(__file__).parent / "trades" / "XXBTZUSD" / "data.csv"
    )
    assert not check_historical_data_filepath(invalid_path_not_binary_file, True)

    invalid_path_invalid_feedcode = (
        Path(__file__).parent / "trades" / "invalid" / "data.bin"
    )
    assert not check_historical_data_filepath(invalid_path_invalid_feedcode, True)

    invalid_path_not_trade_or_snapshot = (
        Path(__file__).parent / "trade" / "XXBTZUSD" / "data.bin"
    )
    assert not check_historical_data_filepath(invalid_path_not_trade_or_snapshot, True)

    invalid_path_not_trade = (
        Path(__file__).parent / "snapshots" / "XXBTZUSD" / "data.bin"
    )
    assert not check_historical_data_filepath(invalid_path_not_trade, True)
