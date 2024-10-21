import pytest
from pysrc.adapters.kraken_future_client import _string_to_history_type, _string_to_taker_side, get_history, get_orderbook
from pysrc.adapters.containers import TakerSide, TradeHistoryType, Orderbook

def test_taker_side_conversion():
    assert _string_to_taker_side("buy") == TakerSide.BUY
    assert _string_to_taker_side("sell") == TakerSide.SELL

def test_history_type_conversion():
    assert _string_to_history_type("fill") == TradeHistoryType.FILL
    assert _string_to_history_type("liquidation") == TradeHistory.LIQUIDATION
    assert _string_to_history_type["assignment"] == TradeHistory.ASSIGNMENT
    assert _string_to_history_type["termination"] == TradeHistory.TERMINATION
    assert _string_to_history_type["block"] == TradeHistory.BLOCK

def test_get_history():
    results = get_history("PI_XBTUSD")
    assert len(results) > 0

def test_get_orderbook():
    results = get_orderbook("PI_XBTUSD")
    assert len(results.asks) > 0
    assert len(results.bids) > 0