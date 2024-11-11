from asyncio import Queue
import json
import os
from typing import Optional, Any
import requests
from datetime import datetime, timedelta
import time
from pysrc.adapters.kraken.historical.updates.containers import (
    MBPBook,
    UpdateDelta,
    OrderEventResponse,
    OrderEventType,
)
from pysrc.adapters.kraken.historical.updates.utils import (
    str_to_order_event_type,
    str_to_order_side,
)
from pysrc.adapters.messages import SnapshotMessage, TradeMessage
from pysrc.util.types import Market, OrderSide

import sys

from collections import deque
from threading import Event, Thread, Condition
import numpy as np
from pyzstd import CParameter, compress, decompress, compress_stream, ZstdCompressor

import struct


class HistoricalUpdatesDataClient:
    def __init__(self, resource_path: str):
        self._resource_path = resource_path
        self._session = requests.Session()

        self._done_getting_order_events = False
        self._done_getting_exec_events = False

        self._order_deltas = deque()
        self._exec_deltas = deque()

        self._order_cond_var = Condition()
        self._exec_cond_var = Condition()

        self._cur_sec = -1

        self._zstd_options = {CParameter.compressionLevel: 10}

        self.i = 0

    def _request(self, route: str, params: dict[str, Any]) -> Any:
        res = self._session.get(route, params=params)
        if res.status_code != 200:
            raise ValueError(f"Failed to get from '{route}', received {res.text}")

        return res.json()

    def _delta_from_order_event(self, e: dict) -> list[UpdateDelta]:
        event_json = e["event"]
        event_type_str = list(event_json.keys())[0]
        event_type = str_to_order_event_type(event_type_str)

        match event_type:
            case OrderEventType.PLACED | OrderEventType.CANCELLED:
                order_json = event_json[event_type_str]["order"]

                return [
                    UpdateDelta(
                        side=str_to_order_side(order_json["direction"]),
                        timestamp=e["timestamp"],
                        sign=1 if event_type == OrderEventType.PLACED else -1,
                        quantity=float(order_json["quantity"]),
                        price=float(order_json["limitPrice"]),
                    )
                ]
            case OrderEventType.UPDATED:
                new_order_json = event_json[event_type_str]["newOrder"]
                old_order_json = event_json[event_type_str]["oldOrder"]

                return [
                    UpdateDelta(
                        side=str_to_order_side(new_order_json["direction"]),
                        timestamp=e["timestamp"],
                        sign=1,
                        quantity=float(new_order_json["quantity"]),
                        price=float(new_order_json["limitPrice"]),
                    ),
                    UpdateDelta(
                        side=str_to_order_side(old_order_json["direction"]),
                        timestamp=e["timestamp"],
                        sign=-1,
                        quantity=float(old_order_json["quantity"]),
                        price=float(old_order_json["limitPrice"]),
                    ),
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

        deltas = []
        for e in res["elements"]:
            deltas.extend(self._delta_from_order_event(e))

        return OrderEventResponse(
            continuation_token=res.get("continuationToken"), deltas=deltas
        )

    def _delta_from_execution_event(self, e: dict) -> list[UpdateDelta]:
        event_json = e["event"]["Execution"]["execution"]

        return [
            UpdateDelta(
                side=OrderSide.BID,
                timestamp=event_json["timestamp"],
                sign=-1,
                quantity=float(event_json["quantity"]),
                price=float(event_json["price"]),
            ),
            UpdateDelta(
                side=OrderSide.ASK,
                timestamp=event_json["timestamp"],
                sign=-1,
                quantity=float(event_json["quantity"]),
                price=float(event_json["price"]),
            ),
        ]

    def _get_execution_events(
        self,
        asset: str,
        since: Optional[int] = None,
        before: Optional[int] = None,
        continuation_token: Optional[str] = None,
    ):
        route = f"https://futures.kraken.com/api/history/v3/market/{asset}/executions"

        params = {
            "sort": "asc",
            "since": since,
            "before": before,
            "continuation_token": continuation_token,
        }

        res = self._request(route, params)

        deltas = []
        for e in res["elements"]:
            deltas.extend(self._delta_from_execution_event(e))

        return OrderEventResponse(
            continuation_token=res.get("continuationToken"), deltas=deltas
        )

    def _queue_events_for_day(
        self,
        asset: str,
        day: datetime,
        should_get_order_events: bool,
    ):
        get_events_func = (
            self._get_order_events
            if should_get_order_events
            else self._get_execution_events
        )
        queue = self._order_deltas if should_get_order_events else self._exec_deltas
        cond_var = (
            self._order_cond_var if should_get_order_events else self._exec_cond_var
        )

        since_time = int(day.timestamp() * 1000)
        before_time = int((day + timedelta(hours=2)).timestamp() * 1000)

        continuation_token = None
        while True:
            order_res = get_events_func(
                asset=asset,
                since=since_time,
                before=before_time,
                continuation_token=continuation_token,
            )

            for d in order_res.deltas:
                queue.append(d)

            with cond_var:
                cond_var.notify()

            continuation_token = order_res.continuation_token
            if not continuation_token:
                break

        if should_get_order_events:
            self._done_getting_order_events = True
        else:
            self._done_getting_exec_events = True

    def _compute_next_snapshot(self) -> Optional[SnapshotMessage]:
        is_last_iter = len(self._order_deltas) > 0 or len(self._exec_deltas) > 0

        while True:
            self.i += 1
            if (not self._order_deltas and self._done_getting_order_events) or (
                not self._exec_deltas and self._done_getting_exec_events
            ):
                break

            if self.i % 10_000 == 0:
                print(f"iter {self.i}")

            with self._order_cond_var:
                self._order_cond_var.wait_for(lambda: len(self._order_deltas))

            with self._exec_cond_var:
                self._exec_cond_var.wait_for(lambda: len(self._exec_deltas))

            if (self._exec_deltas[0].timestamp // 1000) != self._cur_sec and (
                self._order_deltas[0].timestamp // 1000
            ) != self._cur_sec:
                self._cur_sec = min(
                    self._exec_deltas[0].timestamp // 1000,
                    self._order_deltas[0].timestamp // 1000,
                )
                return self._mbp_book.to_snapshot_message(self._cur_sec)
            
            if self._exec_deltas[0].timestamp < self._order_deltas[0].timestamp:
                delta = self._exec_deltas.popleft()
            else:
                delta = self._order_deltas.popleft()

            self._cur_sec = delta.timestamp // 1000

            self._mbp_book.apply_delta(delta)

        while not self._done_getting_order_events or self._order_deltas:
            with self._order_cond_var:
                self._order_cond_var.wait_for(lambda: len(self._order_deltas))

            if (self._order_deltas[0].timestamp // 1000) != self._cur_sec:
                self._cur_sec = self._order_deltas[0].timestamp // 1000
                return self._mbp_book.to_snapshot_message(self._cur_sec)

            delta = self._order_deltas.popleft()
            self._cur_sec = delta.timestamp // 1000

            self._mbp_book.apply_delta(delta)

        while not self._done_getting_exec_events or self._exec_deltas:
            with self._exec_cond_var:
                self._exec_cond_var.wait_for(lambda: len(self._exec_deltas))

            if (self._exec_deltas[0].timestamp // 1000) != self._cur_sec:
                self._cur_sec = self._exec_deltas[0].timestamp // 1000
                return self._mbp_book.to_snapshot_message(self._cur_sec)

            delta = self._exec_deltas.popleft()
            self._cur_sec = delta.timestamp // 1000

            self._mbp_book.apply_delta(delta)

        if is_last_iter:
            return self._mbp_book.to_snapshot_message(self._cur_sec)

        return None

    def _compute_updates_for_day(
        self,
        asset: str,
        day: datetime,
    ):
        file_path = os.path.join(self._resource_path, asset, day.strftime("%m_%d_%Y"))
        c = ZstdCompressor(level_or_option=self._zstd_options)
        f = open(file_path, "wb")

        order_thread = Thread(
            target=self._queue_events_for_day, args=(asset, day, True)
        )
        order_thread.start()

        exec_thread = Thread(
            target=self._queue_events_for_day, args=(asset, day, False)
        )
        exec_thread.start()

        snapshot = self._compute_next_snapshot()
        while snapshot:
            f.write(c.compress(snapshot.to_bytes()))
            snapshot = self._compute_next_snapshot()

        order_thread.join()
        exec_thread.join()

        f.write(c.flush())
        f.close()

    def download_updates(
        self, asset: str, since: datetime, until: Optional[datetime] = None
    ):
        asset_path = os.path.join(self._resource_path, asset)
        if not os.path.exists(asset_path):
            os.mkdir(asset_path)

        if not until:
            until = datetime.now()

        while since.timestamp() < until.timestamp():
            self._mbp_book = MBPBook(feedcode=asset, market=Market.KRAKEN_USD_FUTURE)

            self._done_getting_order_events = False
            self._done_getting_exec_events = False

            self._order_deltas = deque()
            self._exec_deltas = deque()

            self._order_cond_var = Condition()
            self._exec_cond_var = Condition()

            self._cur_sec = since.timestamp()

            self._compute_updates_for_day(asset, since)
            since += timedelta(days=1)
