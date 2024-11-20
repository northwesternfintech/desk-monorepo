import pytest
import numpy as np
import os
import random
from datetime import date

from pysrc.test.helpers import get_resources_path
from pysrc.data_handlers.kraken.historical.trades_data_handler import TradesDataHandler
from pysrc.adapters.messages import TradeMessage
from pysrc.util.types import Market, OrderSide, Asset

random.seed(42)
resource_path = get_resources_path(__file__)


def test_read_write_to_file() -> None:
    handler = TradesDataHandler(resource_path / "trades")

    trades = [
        TradeMessage(1, "XADAZUSD", 1, 10.0, 1.0, OrderSide.BID, Market.KRAKEN_SPOT),
        TradeMessage(2, "XADAZUSD", 1, 10.02, 0.5, OrderSide.BID, Market.KRAKEN_SPOT),
        TradeMessage(10, "XADAZUSD", 1, 9.99, 1.5, OrderSide.BID, Market.KRAKEN_SPOT),
    ]

    test_file_path = resource_path / "trades" / "XADAZUSD" / "test.bin"
    handler.write(test_file_path, trades)
    restored_trades = handler.read(test_file_path)

    assert len(trades) == len(restored_trades)
    for i in range(len(trades)):
        assert trades[i].feedcode == restored_trades[i].feedcode
        assert trades[i].market == restored_trades[i].market
        assert trades[i].n_trades == restored_trades[i].n_trades
        assert trades[i].price == pytest.approx(restored_trades[i].price, rel=1e-7)
        assert trades[i].quantity == pytest.approx(
            restored_trades[i].quantity, rel=1e-7
        )
        assert trades[i].side == restored_trades[i].side
        assert trades[i].time == restored_trades[i].time


def test_stream_data() -> None:
    handler = TradesDataHandler(resource_path / "trades")

    trades = []
    for i in range(10):
        trades.append(
            TradeMessage(
                time=i,
                feedcode="XADAZUSD",
                n_trades=1,
                price=random.uniform(100, 200),
                quantity=random.uniform(0, 10),
                side=OrderSide.BID,
                market=Market.KRAKEN_SPOT,
            )
        )

    test_file_path = resource_path / "trades" / "XADAZUSD" / "test2.bin"
    handler.write(test_file_path, trades)

    gen = handler.stream_read(test_file_path)

    for i in range(len(trades)):
        trade = next(gen)
        assert trade.time == trades[i].time
        assert trade.feedcode == trades[i].feedcode
        assert trade.n_trades == trades[i].n_trades
        assert trade.market == trades[i].market
        assert trade.price == pytest.approx(trades[i].price, rel=1e-7)
        assert trade.quantity == pytest.approx(trades[i].quantity, rel=1e-7)
        assert trade.side == trades[i].side

    with pytest.raises(StopIteration):
        next(gen)
