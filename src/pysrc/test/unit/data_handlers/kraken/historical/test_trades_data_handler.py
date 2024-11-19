import pytest
import numpy as np
import os
from datetime import date

from pysrc.test.helpers import get_resources_path
from pysrc.data_handlers.kraken.historical.trades_data_handler import TradesDataHandler
from pysrc.adapters.messages import TradeMessage
from pysrc.util.types import Market, OrderSide

resource_path = get_resources_path(__file__)


def test_read_write_to_file() -> None:
    handler = TradesDataHandler(resource_path / "trades")

    trades = [
        TradeMessage(1, "BONKUSD", 1, 10.0, 1.0, OrderSide.BID, Market.KRAKEN_SPOT),
        TradeMessage(2, "BONKUSD", 1, 10.02, 0.5, OrderSide.BID, Market.KRAKEN_SPOT),
        TradeMessage(10, "BONKUSD", 1, 9.99, 1.5, OrderSide.BID, Market.KRAKEN_SPOT),
    ]

    test_file_path = resource_path / "trades" / "BONKUSD" / "test.bin"
    handler.write_to_file(test_file_path, trades)
    restored_trades = handler.read_file(test_file_path)

    assert len(trades) == len(restored_trades)
    for i in range(len(trades)):
        assert trades[i].feedcode == restored_trades[i].feedcode
        assert trades[i].market == restored_trades[i].market
        assert trades[i].n_trades == restored_trades[i].n_trades
        assert trades[i].price == restored_trades[i].price
        assert trades[i].quantity == restored_trades[i].quantity
        assert trades[i].side == restored_trades[i].side
        assert trades[i].time == restored_trades[i].time


def test_stream_data() -> None:
    handler = TradesDataHandler(resource_path / "trades")

    csv_path = resource_path / "trades/AEVOEUR/AEVOEUR.csv"
    np_dtype = [("time", "u8"), ("price", "f4"), ("volume", "f4")]
    arr = np.loadtxt(csv_path, delimiter=",", dtype=np_dtype)
    assert arr.shape[0] == 34

    gen = handler.stream_data_2(
        "AEVOEUR",
        date(year=2024, month=6, day=28),
        until=date(year=2024, month=7, day=1),
    )

    for i in range(34):
        trade = next(gen)
        assert trade.feedcode == "AEVOEUR"
        assert trade.n_trades == 1
        assert trade.market == Market.KRAKEN_SPOT
        assert trade.time == arr[i][0]
        assert trade.price == arr[i][1]
        assert trade.quantity == arr[i][2]
        assert trade.side == OrderSide.BID

    with pytest.raises(StopIteration):
        next(gen)
