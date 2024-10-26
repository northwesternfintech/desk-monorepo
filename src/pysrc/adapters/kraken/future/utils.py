from typing import Any

from pysrc.adapters.kraken.future.containers import (
    OrderStatus,
    OrderType,
    PositionSide,
    PriceUnit,
    TriggerSignal,
    TradeHistoryType, 
    TradeHistory
)
from pysrc.util.types import OrderSide


def str_to_position_side(s: str) -> PositionSide:
    return PositionSide[s.upper()]


def position_side_to_str(p: PositionSide) -> str:
    return p.name.lower()


def str_to_order_type(s: str) -> OrderType:
    return OrderType[s.upper()]


def order_type_to_str(o: OrderType) -> str:
    return o.name.lower()


def str_to_order_status(s: str) -> OrderStatus:
    return OrderStatus[s.upper()]


def order_status_to_str(o: OrderStatus) -> str:
    return o.name.lower()


def str_to_trigger_signal(s: str) -> TriggerSignal:
    return TriggerSignal[s.upper()]


def trigger_signal_to_str(t: TriggerSignal) -> str:
    return t.name.lower()


def str_to_order_side(s: str) -> OrderSide:
    match s:
        case "buy":
            return OrderSide.BID
        case "sell":
            return OrderSide.ASK
        case _:
            raise ValueError(f"Can't convert '{s}' to OrderSide")


def order_side_to_str(o: OrderSide) -> str:
    match o:
        case OrderSide.BID:
            return "buy"
        case OrderSide.ASK:
            return "sell"


def str_to_price_unit(s: str) -> PriceUnit:
    return PriceUnit[s.upper()]


def price_unit_to_str(p: PriceUnit) -> str:
    return p.name.lower()


def remove_empty_values(d: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for k, v in d.items():
        if v is None:
            continue

        if isinstance(v, dict):
            cleaned[k] = remove_empty_values(v)
        elif isinstance(v, list):
            cleaned[k] = [
                remove_empty_values(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            cleaned[k] = v

    return cleaned


def kraken_encode_dict(d: dict[str, Any]) -> str:
    cleaned = remove_empty_values(d)

    encoded_items = []
    for k, v in cleaned.items():
        encoded_item = None

        if isinstance(v, list):
            encoded_item = f"{k}={','.join(v)}"
        else:
            encoded_item = f"{k}={v}"

        encoded_items.append(encoded_item)

    return "&".join(encoded_items)


def string_to_history_type(history_type: str) -> TradeHistoryType:
    try:
        return TradeHistoryType[history_type.upper()]
    except KeyError:
        return None

def serialize_history(symbol: str, hist: dict) -> TradeHistory:
    return TradeHistory(
        symbol = symbol,
        price = hist.get("price", 0),
        time = hist.get("time", ""),
        trade_id = hist.get("trade_id", 0),
        side = str_to_order_side(hist.get("side", "")),
        size = hist.get("size"),
        historyType = string_to_history_type(hist.get("type", "")),
        uid = hist.get("uid"),
        instrument_identification_type = hist.get("instrument_identification_type"),
        isin = hist.get("isin"),
        execution_venue = hist.get("execution_venue"),
        price_notation = hist.get("price_notation"),
        price_currency = hist.get("price_currency"),
        notional_amount = hist.get("notional_amount"),
        notional_currency = hist.get("notional_currency"),
        publication_time = hist.get("publication_time"),
        publication_venue = hist.get("publication_venue"),
        transaction_identification_code = hist.get("transaction_identification_code"),
        to_be_cleared = hist.get("to_be_cleared")
    )