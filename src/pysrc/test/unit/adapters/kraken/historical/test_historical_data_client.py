from datetime import datetime
import os
from pysrc.adapters.kraken.historical.historical_data_client import HistoricalDataClient
from pysrc.test.helpers import get_resources_path
import numpy as np
from pysrc.util.types import Market

resource_path = str(get_resources_path(__file__))


def test_chunking() -> None:
    test_file_path = os.path.join(resource_path, "BONKUSD", "test.csv")
    client = HistoricalDataClient()
    chunked_files = client._chunk_csv_by_day(test_file_path)

    expected_chunked_files = [
        os.path.join(resource_path, "BONKUSD", "07_01_2024.csv"),
        os.path.join(resource_path, "BONKUSD", "07_04_2024.csv"),
        os.path.join(resource_path, "BONKUSD", "07_08_2024.csv"),
    ]

    assert set(chunked_files) == set(chunked_files)

    with open(expected_chunked_files[0]) as f:
        lines = [line.strip() for line in f.readlines()]
        assert len(lines) == 1
        assert lines[0] == "1719792015,2.387,7.49855066"

    with open(expected_chunked_files[1]) as f:
        lines = [line.strip() for line in f.readlines()]
        assert len(lines) == 1
        assert lines[0] == "1720082973,2.319,6.49440501"

    with open(expected_chunked_files[2]) as f:
        lines = [line.strip() for line in f.readlines()]
        assert len(lines) == 4
        assert lines[0] == "1720421999,1.818,44"
        assert lines[1] == "1720423482,1.633,7"
        assert lines[2] == "1720423511,1.621,167.5241759"
        assert lines[3] == "1720423511,1.618,1.5"

    for file_path in expected_chunked_files:
        os.remove(file_path)


def test_serialization() -> None:
    test_file_path = os.path.join(resource_path, "BONKUSD", "test.csv")
    client = HistoricalDataClient()

    serialized_file_path = client._serialize_csv(test_file_path)
    trades = client.get_trades_from_file(serialized_file_path)

    assert len(trades) == 6

    assert trades[0].market == Market.KRAKEN_SPOT
    assert trades[0].feedcode == "BONKUSD"

    assert np.isclose(
        [trades[0].time, trades[0].price, trades[0].quantity],
        [1719792015, 2.387, 7.49855066],
    ).all()

    assert np.isclose(
        [trades[1].time, trades[1].price, trades[1].quantity],
        [1720082973, 2.319, 6.49440501],
    ).all()

    assert np.isclose(
        [trades[2].time, trades[2].price, trades[2].quantity], [1720421999, 1.818, 44]
    ).all()

    assert np.isclose(
        [trades[3].time, trades[3].price, trades[3].quantity], [1720423482, 1.633, 7]
    ).all()

    assert np.isclose(
        [trades[4].time, trades[4].price, trades[4].quantity],
        [1720423511, 1.621, 167.5241759],
    ).all()

    assert np.isclose(
        [trades[5].time, trades[5].price, trades[5].quantity], [1720423511, 1.618, 1.5]
    ).all()

    os.remove(serialized_file_path)


def test_get_trades() -> None:
    test_file_path = os.path.join(resource_path, "BONKUSD", "test.csv")
    client = HistoricalDataClient()
    chunked_files = client._chunk_csv_by_day(test_file_path)

    chunked_file = os.path.join(resource_path, "BONKUSD", "07_01_2024.csv")
    serialized_file_path = client._serialize_csv(chunked_file)
    trades = client.get_trades("BONKUSD", datetime(2024, 7, 1), resource_path)

    assert len(trades) == 1

    assert trades[0].market == Market.KRAKEN_SPOT
    assert trades[0].feedcode == "BONKUSD"

    assert np.isclose(
        [trades[0].time, trades[0].price, trades[0].quantity],
        [1719792015, 2.387, 7.49855066],
    ).all()

    trades = client.get_trades("BONKUSD", datetime(2025, 7, 1), resource_path)
    assert len(trades) == 0

    os.remove(serialized_file_path)
    for file_path in chunked_files:
        os.remove(file_path)
