from pathlib import Path

import pytest

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
    resource_path = Path(__file__).parent
    invalid_path_not_file = resource_path / "trades" / "XXBTZUSD"
    assert not check_historical_data_filepath(invalid_path_not_file, True)

    invalid_path_not_binary_file = resource_path / "XXBTZUSD" / "data.csv"
    assert not check_historical_data_filepath(invalid_path_not_binary_file, True)

    invalid_path_invalid_feedcode = resource_path / "trades" / "invalid" / "data.bin"
    assert not check_historical_data_filepath(invalid_path_invalid_feedcode, True)

    invalid_path_not_trade_or_snapshot = (
        resource_path / "trade" / "XXBTZUSD" / "data.bin"
    )
    assert not check_historical_data_filepath(invalid_path_not_trade_or_snapshot, True)

    invalid_path_not_trade = resource_path / "snapshots" / "XXBTZUSD" / "data.bin"
    assert not check_historical_data_filepath(invalid_path_not_trade, True)
