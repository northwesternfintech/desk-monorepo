import pytest
from pysrc.adapters.kraken.future.containers import TakerSide, TradeHistoryType, TradeHistory
from pysrc.adapters.kraken.future.utils import string_to_taker_side, string_to_history_type

def test_taker_side_conversion() -> None:
    assert string_to_taker_side("buy") == TakerSide.BUY
    assert string_to_taker_side("sell") == TakerSide.SELL

def test_history_type_conversion() -> None:
    assert string_to_history_type("fill") == TradeHistoryType.FILL
    assert string_to_history_type("liquidation") == TradeHistoryType.LIQUIDATION
    assert string_to_history_type("assignment") == TradeHistoryType.ASSIGNMENT
    assert string_to_history_type("termination") == TradeHistoryType.TERMINATION
    assert string_to_history_type("block") == TradeHistoryType.BLOCK