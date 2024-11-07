import json
import os
from typing import Optional, Any
import requests
from datetime import datetime, timedelta

from pysrc.adapters.kraken.historical.updates.containers import (
    UpdateDelta,
    OrderEventResponse,
    OrderEventType,
)
from pysrc.adapters.kraken.historical.updates.utils import str_to_order_event_type, str_to_order_side
from pysrc.adapters.messages import TradeMessage
from pysrc.util.types import OrderSide

import sys


class HistoricalUpdatesDataClient:
    def __init__(self, resource_path: str):
        self._resource_path = resource_path
        self._session = requests.Session()

    def _request(self, route: str, params: dict[str, Any]) -> Any:
        res = self._session.get(route, params=params)
        if res.status_code != 200:
            raise ValueError(f"Failed to get from '{route}', received {res.text}")

        return res.json()

    def _delta_from_json(self, e: dict) -> list[UpdateDelta]:
        event_json = e["event"]
        event_type_str = list(event_json.keys())[0]
        event_type = str_to_order_event_type(event_type_str)

        match event_type:
            case OrderEventType.PLACED | OrderEventType.CANCELLED:
                order_json = event_json[event_type_str]["order"]

                return [
                    UpdateDelta(
                    side=str_to_order_side(order_json["direction"]),
                    sign=1 if event_type == OrderEventType.PLACED else -1,
                    quantity=float(order_json["quantity"]),
                    price=float(order_json["limitPrice"]))
                ]
            case OrderEventType.UPDATED:
                new_order_json = event_json[event_type_str]["newOrder"]
                old_order_json = event_json[event_type_str]["oldOrder"]

                return [
                    UpdateDelta(
                    side=str_to_order_side(new_order_json["direction"]),
                    sign=1,
                    quantity=float(new_order_json["quantity"]),
                    price=float(new_order_json["limitPrice"])),
                    UpdateDelta(
                    side=str_to_order_side(old_order_json["direction"]),
                    sign=-1,
                    quantity=float(old_order_json["quantity"]),
                    price=float(old_order_json["limitPrice"])),
                ]
            case OrderEventType.REJECTED | OrderEventType.EDIT_REJECTED:
                return []
            case _:
                raise ValueError(f"Received malformed event {e}")

    def _get_order_events(
        self,
        asset: str,
        since: Optional[int] = None,
        before: Optional[int] = None,
        continuation_token: Optional[str] = None,
    ):
        route = f"https://futures.kraken.com/api/history/v3/market/{asset}/orders"

        params = {
            "sort": "asc",
            "since": since,
            "before": before,
            "continuation_token": continuation_token,
        }

        res = self._request(route, params)

        # print(json.dumps(res, indent=4))

        deltas = []
        for e in res["elements"]:
            deltas.extend(self._delta_from_json(e))

        return OrderEventResponse(
            continuation_token=res.get("continuationToken"), deltas=deltas
        )
    
    # def _apply_order_events(
    #         self,
    #         current_orders: list[dict[str, tuple[float, float]]],
    #         events: list[OrderEvent]
    # ) -> None:
    #     for e in events:
    #         match e.event_type:
    #             case OrderEventType.PLACED:
    #                 new_trade = [
    #                     e.price,
    #                     e.quantity
    #                 ]

    #                 current_orders[e.side][e.uid] = new_trade
    #             case OrderEventType.UPDATED:
    #                 if e.quantity == 0:
    #                     print("HERE!")
    #                     current_orders[e.side].pop(e.uid, None)
    #                     continue

    #                 new_trade = [
    #                     e.price,
    #                     e.quantity
    #                 ]

    #                 current_orders[e.side][e.uid] = new_trade
    #             case OrderEventType.CANCELLED:
    #                 current_orders[e.side].pop(e.uid, None)

    # def _compute_updates_for_day(
    #         self,
    #         asset: str,
    #         day: datetime,
    #         cur_trades
    # ):
    #     since_time = int(day.timestamp() * 1000)
    #     before_time = int((day + timedelta(days=1)).timestamp() * 1000)

    #     res = self._get_order_events(
    #         asset=asset,
    #         since=since_time,
    #         before=before_time
    #     )

    #     events = res.events
    #     continuation_token = res.continuation_token
    #     x = 0
    #     while events:
    #         x += 1
    #         if (x % 100 == 0):
    #             print(f"{x} iterations")
    #             print(
    #                 f"cur_trades has {len(cur_trades[OrderSide.BID])} bids and {len(cur_trades[OrderSide.ASK])} asks"
    #             )
    #         if continuation_token and events[0].timestamp == events[-1].timestamp:
    #             res = self._get_order_events(
    #                 asset=asset,
    #                 since=since_time,
    #                 before=before_time,
    #                 continuation_token=continuation_token
    #             )

    #             events.extend(res.events)
    #             continuation_token = res.continuation_token

    #         next_sec_idx = 1
    #         for i, event in enumerate(events):
    #             if event.timestamp > events[0].timestamp:
    #                 next_sec_idx = i
    #                 break
    #         self._apply_order_events(
    #             cur_trades,
    #             events[:next_sec_idx]
    #         )
    #         events = events[next_sec_idx:]

    #     print(cur_trades)

    # def download_updates(
    #         self,
    #         asset: str,
    #         since: datetime,
    #         until: Optional[datetime] = None
    # ):
    #     asset_path = os.path.join(self._resource_path, asset)
    #     if not os.path.exists(asset_path):
    #         os.mkdir(asset_path)

    #     if not until:
    #         until = datetime.now()

    #     num_days = (until - since).days()

    #     cur_trades = {
    #         OrderSide.ASK: {},
    #         OrderSide.BID: {}
    #     }

    #     day_events = []
    #     for i in range(num_days):
    #         cur_day = since + timedelta(days=i)
    #         next_day = cur_day + timedelta(days=1)

            


        



        