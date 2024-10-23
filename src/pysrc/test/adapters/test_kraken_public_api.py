import pytest
from pysrc.adapters.kraken.future.kraken_future_client import KrakenFutureClient
from pysrc.adapters.kraken.future.containers import TakerSide, TradeHistoryType, Orderbook, TradeHistory

def test_taker_side_conversion() -> None:
    client = KrakenFutureClient("", "")
    assert client._string_to_taker_side("buy") == TakerSide.BUY
    assert client._string_to_taker_side("sell") == TakerSide.SELL

def test_history_type_conversion() -> None:
    client = KrakenFutureClient("", "")
    assert client._string_to_history_type("fill") == TradeHistoryType.FILL
    assert client._string_to_history_type("liquidation") == TradeHistoryType.LIQUIDATION
    assert client._string_to_history_type("assignment") == TradeHistoryType.ASSIGNMENT
    assert client._string_to_history_type("termination") == TradeHistoryType.TERMINATION
    assert client._string_to_history_type("block") == TradeHistoryType.BLOCK

def test_get_history() -> None:
    client = KrakenFutureClient("", "")
    results = client.get_history("PI_XBTUSD")
    assert len(results) > 0

def test_get_orderbook() -> None:
    client = KrakenFutureClient("", "")
    results = client.get_orderbook("PI_XBTUSD")
    assert len(results.asks) > 0
    assert len(results.bids) > 0