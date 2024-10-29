from typing import Any
from pysrc.adapters.kraken.future.containers import (
    OrderStatus,
    OrderType,
    PositionSide,
    PriceUnit,
    TriggerSignal,
    TradeHistoryType,
    TradeHistory,
)
from pysrc.adapters.kraken.future.utils import (
    kraken_encode_dict,
    order_side_to_str,
    order_status_to_str,
    order_type_to_str,
    position_side_to_str,
    price_unit_to_str,
    remove_empty_values_from_dict,
    str_to_order_side,
    str_to_order_status,
    str_to_order_type,
    str_to_position_side,
    str_to_price_unit,
    str_to_trigger_signal,
    trigger_signal_to_str,
    string_to_history_type,
)
from pysrc.util.types import OrderSide

import pytest


def test_remove_empty_values() -> None:
    d = {"a": 1, "b": None, "c": "", "d": 0}
    assert remove_empty_values_from_dict(d) == {"a": 1, "c": "", "d": 0}

    e = {
        "a": 1,
        "b": [
            {"a": 1, "b": None},
            {"a": 1, "b": None},
        ],
        "c": 10,
    }
    assert remove_empty_values_from_dict(e) == {
        "a": 1,
        "b": [
            {"a": 1},
            {"a": 1},
        ],
        "c": 10,
    }

    f = {"a": 1, "b": {"a": 1, "b": None}, "c": 10}
    assert remove_empty_values_from_dict(f) == {"a": 1, "b": {"a": 1}, "c": 10}


def test_kraken_encode_dict() -> None:
    d = {"a": 1, "b": 2, "c": None}
    assert kraken_encode_dict(d) == "a=1&b=2"

    e = {"a": 1, "b": 2, "c": 3, "d": {"a": 1, "b": 2}}
    assert kraken_encode_dict(e) == "a=1&b=2&c=3&d={'a': 1, 'b': 2}"


def test_position_side_conversion() -> None:
    for position_side in PositionSide:
        assert position_side == str_to_position_side(
            position_side_to_str(position_side)
        )

    with pytest.raises(Exception):
        str_to_position_side("")


def test_order_type_conversion() -> None:
    for order_type in OrderType:
        assert order_type == str_to_order_type(order_type_to_str(order_type))

    with pytest.raises(Exception):
        str_to_order_type("")


def test_order_status_conversion() -> None:
    for order_status in OrderStatus:
        assert order_status == str_to_order_status(order_status_to_str(order_status))

    with pytest.raises(Exception):
        str_to_order_status("")


def test_trigger_signal_conversion() -> None:
    for trigger_signal in TriggerSignal:
        assert trigger_signal == str_to_trigger_signal(
            trigger_signal_to_str(trigger_signal)
        )

    with pytest.raises(Exception):
        str_to_trigger_signal("")


def test_order_side_conversion() -> None:
    for order_side in OrderSide:
        assert order_side == str_to_order_side(order_side_to_str(order_side))

    with pytest.raises(Exception):
        str_to_order_side("")


def test_price_unit_conversion() -> None:
    for price_unit in PriceUnit:
        assert price_unit == str_to_price_unit(price_unit_to_str(price_unit))

    with pytest.raises(Exception):
        str_to_price_unit("")


def test_history_type_conversion() -> None:
    assert string_to_history_type("fill") == TradeHistoryType.FILL
    assert string_to_history_type("liquidation") == TradeHistoryType.LIQUIDATION
    assert string_to_history_type("assignment") == TradeHistoryType.ASSIGNMENT
    assert string_to_history_type("termination") == TradeHistoryType.TERMINATION
    assert string_to_history_type("block") == TradeHistoryType.BLOCK
    with pytest.raises(KeyError):
        string_to_history_type("john") is None
