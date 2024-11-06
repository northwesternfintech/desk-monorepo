from typing import Optional, Any
import requests
import json

from pysrc.adapters.kraken.historical.updates.containers import (
    OrderEvent,
    OrderEventResponse,
    OrderEventType,
)
from pysrc.adapters.kraken.historical.updates.utils import str_to_order_event_type, str_to_order_side


class HistoricalUpdatesDataClient:
    def __init__(self, resource_path: str):
        self._resource_path = resource_path
        self._session = requests.Session()

    def _request(self, route: str, params: dict[str, Any]) -> Any:
        res = self._session.get(route, params=params)
        if res.status_code != 200:
            raise ValueError(f"Failed to get from '{route}', received {res.text}")

        return res.json()

    def _event_from_json(self, e: dict) -> OrderEvent:
        event_json = e["event"]
        event_type_str = list(event_json.keys())[0]
        event_type = str_to_order_event_type(event_type_str)

        match event_type:
            case OrderEventType.PLACED:
                order_json = event_json[event_type_str]["order"]
            case OrderEventType.UPDATED:
                order_json = event_json[event_type_str]["newOrder"]
            case OrderEventType.CANCELLED:
                order_json = event_json[event_type_str]["order"]
            case _:
                raise ValueError(f"Received malformed event {e}")

        return OrderEvent(
            event_type=event_type,
            uid=e["uid"],
            timestamp=e["timestamp"],
            side=str_to_order_side(order_json["direction"]),
            quantity=float(order_json["quantity"]),
            price=float(order_json["limitPrice"]),
        )

    def _get_order_events(
        self,
        asset: str,
        since: Optional[int] = None,
        continuation_token: Optional[str] = None,
    ):
        route = f"https://futures.kraken.com/api/history/v3/market/{asset}/orders"

        params = {
            "sort": "asc",
            "since": since,
            "continuation_token": continuation_token,
        }

        res = self._request(route, params)

        events = []
        for e in res["elements"]:
            events.append(self._event_from_json(e))

        return OrderEventResponse(
            continuation_token=res.get("continuation_token"), events=events
        )
