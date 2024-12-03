import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from threading import Thread
from typing import Any, Optional

import requests

from pysrc.adapters.kraken.asset_mappings import asset_to_kraken
from pysrc.adapters.kraken.historical.updates.containers import (
    ChunkedEventQueue,
    EventType,
    MBPBook,
    OrderEventResponse,
    OrderEventType,
    UpdateDelta,
)
from pysrc.adapters.kraken.historical.updates.utils import (
    str_to_order_event_type,
    str_to_order_side,
)
from pysrc.adapters.messages import SnapshotMessage
from pysrc.data_handlers.kraken.historical.snapshots_data_handler import (
    SnapshotsDataHandler,
)
from pysrc.util.exceptions import DIE
from pysrc.util.types import Asset, Market, OrderSide


class HistoricalUpdatesDataClient:
    def __init__(self, resource_path: str):
        self._resource_path = resource_path
        self._session = requests.Session()

        self._NUM_CHUNKS = 48
        self._queue = ChunkedEventQueue(num_chunks=self._NUM_CHUNKS)
        self._last_saved_mbp_book: Optional[MBPBook] = None
        self._cur_mbp_book: Optional[MBPBook] = None
        self._last_saved_sec = -1
        self._cur_sec = -1

        self._snapshot_handler = SnapshotsDataHandler()

    def _request(self, route: str, params: dict[str, Any]) -> Any:
        res = self._session.get(route, params=params)
        if res.status_code != 200:
            DIE(f"Failed to get from '{route}', received {res.text}")

        return res.json()

    def _delta_from_order_event(self, e: dict) -> Optional[UpdateDelta]:
        event_json = e["event"]
        event_type_str = list(event_json.keys())[0]
        event_type = str_to_order_event_type(event_type_str)

        match event_type:
            case OrderEventType.PLACED | OrderEventType.CANCELLED:
                order_json = event_json[event_type_str]["order"]

                quantity = float(order_json["quantity"]) * (
                    1 if event_type == OrderEventType.PLACED else -1
                )
                price = float(order_json["limitPrice"])

                delta = UpdateDelta(
                    side=str_to_order_side(order_json["direction"]),
                    timestamp=e["timestamp"] // 1000,
                    price=price,
                    quantity=quantity,
                )

                return delta
            case OrderEventType.UPDATED:
                new_order_json = event_json[event_type_str]["newOrder"]
                old_order_json = event_json[event_type_str]["oldOrder"]

                new_quantity = float(new_order_json["quantity"])
                new_price = float(new_order_json["limitPrice"])

                delta = UpdateDelta(
                    side=str_to_order_side(new_order_json["direction"]),
                    timestamp=e["timestamp"] // 1000,
                    price=new_price,
                    quantity=new_quantity,
                )

                old_quantity = -1 * float(old_order_json["quantity"])
                old_price = float(old_order_json["limitPrice"])
                delta.add(old_price, old_quantity)

                return delta
            case OrderEventType.REJECTED | OrderEventType.EDIT_REJECTED:
                return None
            case _:
                DIE(f"Received malformed event {e}")

    def _get_order_events(
        self,
        kraken_asset: str,
        since: Optional[int] = None,
        before: Optional[int] = None,
        continuation_token: Optional[str] = None,
    ) -> OrderEventResponse:
        route = (
            f"https://futures.kraken.com/api/history/v3/market/{kraken_asset}/orders"
        )

        params = {
            "sort": "asc",
            "since": since,
            "before": before,
            "continuation_token": continuation_token,
        }

        res = self._request(route, params)

        deltas = [UpdateDelta(OrderSide.BID, -1, 0, 0)]
        for e in res["elements"]:
            delta = self._delta_from_order_event(e)
            if delta:
                if (
                    delta.timestamp == deltas[-1].timestamp
                    and delta.side == deltas[-1].side
                ):
                    deltas[-1].add_delta(delta)
                else:
                    deltas.append(delta)

        return OrderEventResponse(
            continuation_token=res.get("continuationToken"), deltas=deltas[1:]
        )

    def _delta_from_execution_event(self, e: dict) -> list[UpdateDelta]:
        event_json = e["event"]["Execution"]["execution"]

        bid_quantity = -1 * float(event_json["quantity"])
        bid_price = float(event_json["price"])

        bid_delta = UpdateDelta(
            side=OrderSide.BID,
            timestamp=event_json["timestamp"] // 1000,
            price=bid_price,
            quantity=bid_quantity,
        )

        ask_delta = UpdateDelta(
            side=OrderSide.ASK,
            timestamp=bid_delta.timestamp,
            price=bid_price,
            quantity=bid_quantity,
        )

        return [bid_delta, ask_delta]

    def _get_execution_events(
        self,
        kraken_asset: str,
        since: Optional[int] = None,
        before: Optional[int] = None,
        continuation_token: Optional[str] = None,
    ) -> OrderEventResponse:
        route = f"https://futures.kraken.com/api/history/v3/market/{kraken_asset}/executions"

        params = {
            "sort": "asc",
            "since": since,
            "before": before,
            "continuation_token": continuation_token,
        }

        res = self._request(route, params)

        deltas = [UpdateDelta(OrderSide.BID, -1, 0, 0)]
        for e in res["elements"]:
            for delta in self._delta_from_execution_event(e):
                if (
                    delta.timestamp == deltas[-1].timestamp
                    and delta.side == deltas[-1].side
                ):
                    deltas[-1].add_delta(delta)
                else:
                    deltas.append(delta)

        return OrderEventResponse(
            continuation_token=res.get("continuationToken"), deltas=deltas[1:]
        )

    def _queue_events_for_chunk(
        self,
        kraken_asset: str,
        since: datetime,
        until: datetime,
        chunk_idx: int,
        event_type: EventType,
    ) -> None:
        match event_type:
            case EventType.ORDER:
                get_events_func = self._get_order_events
            case EventType.EXECUTION:
                get_events_func = self._get_execution_events

        since_time = int(since.timestamp() * 1000)
        before_time = int(until.timestamp() * 1000)

        try:
            continuation_token = None

            while not self._queue.failed():
                order_res = get_events_func(
                    kraken_asset=kraken_asset,
                    since=since_time,
                    before=before_time,
                    continuation_token=continuation_token,
                )

                self._queue.put(order_res.deltas, event_type, chunk_idx)

                continuation_token = order_res.continuation_token
                if not continuation_token:
                    break

            self._queue.mark_done(event_type, chunk_idx)
        except Exception as _:
            self._queue.mark_failed()

    def _compute_next_snapshot(self) -> Optional[SnapshotMessage]:
        assert self._cur_mbp_book

        is_last_iter = not self._queue.empty()

        while True:
            next_delta = self._queue.peek()
            if next_delta is None:
                break

            if next_delta.timestamp != self._cur_sec:
                prev_sec = self._cur_sec
                self._cur_sec = next_delta.timestamp
                return self._cur_mbp_book.to_snapshot_message(prev_sec)

            delta = self._queue.get()
            if delta is None:
                break

            self._cur_sec = delta.timestamp
            self._cur_mbp_book.apply_delta(delta)

        if is_last_iter and not self._queue.failed():
            return self._cur_mbp_book.to_snapshot_message(self._cur_sec)

        return None

    def _compute_updates_for_day(
        self,
        kraken_asset: str,
        day: datetime,
    ) -> Path:
        snapshot_path = Path(self._resource_path) / "snapshots" / kraken_asset
        if not os.path.exists(snapshot_path):
            os.makedirs(snapshot_path)

        threads = []
        for i in range(self._NUM_CHUNKS):
            order_thread = Thread(
                target=self._queue_events_for_chunk,
                args=(
                    kraken_asset,
                    day + timedelta(minutes=30 * i),
                    day + timedelta(minutes=30 * (i + 1)),
                    i,
                    EventType.ORDER,
                ),
            )

            exec_thread = Thread(
                target=self._queue_events_for_chunk,
                args=(
                    kraken_asset,
                    day + timedelta(minutes=30 * i),
                    day + timedelta(minutes=30 * (i + 1)),
                    i,
                    EventType.EXECUTION,
                ),
            )

            threads.append(order_thread)
            threads.append(exec_thread)

        for thread in threads:
            thread.start()

        snapshots = []
        snapshot = self._compute_next_snapshot()
        while snapshot:
            snapshots.append(snapshot)
            snapshot = self._compute_next_snapshot()

        file_path = snapshot_path / f"{day.strftime('%m_%d_%Y')}.bin"
        self._snapshot_handler.write(file_path, snapshots)

        for thread in threads:
            thread.join()

        return file_path

    def download_updates(
        self,
        asset: Asset,
        since: datetime,
        until: Optional[datetime] = None,
        max_retry_count: Optional[int] = 3,
    ) -> None:
        self._start_time = time.time()
        if max_retry_count is None:
            max_retry_count = 3

        if not until:
            until = datetime.today()

        kraken_asset = asset_to_kraken(asset, Market.KRAKEN_USD_FUTURE)

        self._last_saved_mbp_book = MBPBook(
            feedcode=kraken_asset, market=Market.KRAKEN_USD_FUTURE
        )
        self._last_saved_sec = int(since.timestamp())

        self._cur_mbp_book = MBPBook(
            feedcode=kraken_asset, market=Market.KRAKEN_USD_FUTURE
        )
        self._cur_sec = int(since.timestamp())

        for i in range((until - since).days):
            succeeded = True

            cur = since + timedelta(days=i)
            for _ in range(max_retry_count):
                succeeded = True

                self._queue = ChunkedEventQueue(num_chunks=self._NUM_CHUNKS)
                update_file_path = self._compute_updates_for_day(kraken_asset, cur)

                if self._queue.failed():
                    succeeded = False

                    self._cur_mbp_book = self._last_saved_mbp_book.copy()
                    self._cur_sec = self._last_saved_sec

                    os.remove(update_file_path)
                else:
                    self._last_saved_mbp_book = self._cur_mbp_book.copy()
                    self._last_saved_sec = self._cur_sec

                    break

            if not succeeded:
                failed_day_str = cur.strftime("%m_%d_%Y")
                raise RuntimeError(
                    f"Failed to download updates for '{kraken_asset}' for date '{failed_day_str}'"
                )
