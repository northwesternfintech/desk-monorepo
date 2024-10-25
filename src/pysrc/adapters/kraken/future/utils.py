import urllib

from pysrc.adapters.kraken.future.containers import (
    OrderStatus,
    OrderType,
    PositionSide,
    PriceUnit,
    TriggerSignal,
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


def remove_empty_values(d: dict[str]) -> dict[str]:
    cleaned = {}
    for k, v in d.items():
        if v is None:
            continue

        if isinstance(v, dict):
            cleaned[k] = remove_empty_values(v)
        elif isinstance(v, list):
            cleaned[k] = [remove_empty_values(item) for item in v]
        else:
            cleaned[k] = v

    return cleaned


def kraken_encode_dict(d: dict[str]) -> str:
    cleaned = remove_empty_values(d)

    encoded_items = []
    for k, v in cleaned.items():
        encoded_item = f"{k}={v}"
        encoded_items.append(encoded_item)

    return "&".join(encoded_items)
