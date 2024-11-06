from pysrc.adapters.kraken.historical.updates.containers import OrderEventType
from pysrc.util.types import OrderSide


def str_to_order_event_type(s: str) -> OrderEventType:
    match s:
        case "OrderPlaced":
            return OrderEventType.PLACED
        case "OrderUpdated":
            return OrderEventType.UPDATED
        case "OrderCancelled":
            return OrderEventType.CANCELLED
        case _:
            raise ValueError(f"Unknown order event type {s}")
        
def str_to_order_side(s: str) -> OrderSide:
    match s:
        case "Buy":
            return OrderSide.BID
        case "Sell":
            return OrderSide.ASK
        case _:
            raise ValueError(f"Can't convert '{s}' to OrderSide")
