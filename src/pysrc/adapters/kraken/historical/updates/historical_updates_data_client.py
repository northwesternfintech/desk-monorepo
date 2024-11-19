from io import BufferedIOBase
import os
import struct
from collections import deque
from datetime import datetime, timedelta
from threading import Condition, Thread
from typing import Any, Generator, Optional

import numpy as np
import requests
from pyzstd import CParameter, EndlessZstdDecompressor, ZstdCompressor

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
from pysrc.util.types import Market, OrderSide


class HistoricalUpdatesDataClient:
    def __init__(self, resource_path: str):
        self._resource_path = resource_path
        self._session = requests.Session()

        self._NUM_CHUNKS = 24
        self._queue = ChunkedEventQueue(num_chunks=self._NUM_CHUNKS)
        self._last_saved_mbp_book = None
        self._cur_mbp_book = None
        self._last_saved_sec = -1
        self._cur_sec = -1

        self._zstd_options = {CParameter.compressionLevel: 10}
        self._decompress_buffer = b''

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
                        timestamp=e["timestamp"] // 1000,
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
                        timestamp=e["timestamp"] // 1000,
                        sign=1,
                        quantity=float(new_order_json["quantity"]),
                        price=float(new_order_json["limitPrice"]),
                    ),
                    UpdateDelta(
                        side=str_to_order_side(old_order_json["direction"]),
                        timestamp=e["timestamp"] // 1000,
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
    ) -> OrderEventResponse:
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
                timestamp=event_json["timestamp"] // 1000,
                sign=-1,
                quantity=float(event_json["quantity"]),
                price=float(event_json["price"]),
            ),
            UpdateDelta(
                side=OrderSide.ASK,
                timestamp=event_json["timestamp"] // 1000,
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
    ) -> OrderEventResponse:
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

    def _queue_events_for_chunk(
        self,
        asset: str,
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
            while True:
                order_res = get_events_func(
                    asset=asset,
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
            self._cur_sec = delta.timestamp
            self._cur_mbp_book.apply_delta(delta)

        if is_last_iter and not self._queue.failed():
            return self._cur_mbp_book.to_snapshot_message(self._cur_sec)

        return None

    def _compute_updates_for_day(
        self,
        asset: str,
        day: datetime,
    ) -> str:
        file_path = os.path.join(self._resource_path, asset, day.strftime("%m_%d_%Y"))
        compressor = ZstdCompressor(level_or_option=self._zstd_options)

        f = open(file_path, "wb")

        threads = []
        for i in range(self._NUM_CHUNKS):
            order_thread = Thread(
                target=self._queue_events_for_chunk,
                args=(
                    asset,
                    day + timedelta(hours=i),
                    day + timedelta(hours=i + 1),
                    i,
                    EventType.ORDER
                )
            )

            exec_thread = Thread(
                target=self._queue_events_for_chunk,
                args=(
                    asset,
                    day + timedelta(hours=i),
                    day + timedelta(hours=i + 1),
                    i,
                    EventType.EXECUTION
                )
            )

            threads.append(order_thread)
            threads.append(exec_thread)

        for thread in threads:
            thread.start()

        snapshot = self._compute_next_snapshot()
        while snapshot:
            f.write(compressor.compress(snapshot.to_bytes()))
            snapshot = self._compute_next_snapshot()

        f.write(compressor.flush())
        f.close()

        for thread in threads:
            thread.join()

        return file_path

    def download_updates(
        self, asset: str, since: datetime, until: Optional[datetime] = None, max_retry_count: Optional[int] = 3
    ) -> None:
        asset_path = os.path.join(self._resource_path, asset)
        if not os.path.exists(asset_path):
            os.mkdir(asset_path)

        if not until:
            until = datetime.today()

        self._last_saved_mbp_book = MBPBook(feedcode=asset, market=Market.KRAKEN_USD_FUTURE)
        self._last_saved_sec = int(since.timestamp())

        self._cur_mbp_book = MBPBook(feedcode=asset, market=Market.KRAKEN_USD_FUTURE)
        self._cur_sec = int(since.timestamp())

        for i in range((until - since).days):
            succeeded = True

            cur = since + timedelta(days=i)
            for _ in range(max_retry_count):
                self._queue = ChunkedEventQueue(num_chunks=self._NUM_CHUNKS)
                update_file_path = self._compute_updates_for_day(asset, cur)

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
                raise ValueError(f"Failed to download updates for '{asset}' for date '{failed_day_str}'")

    def _decompress_bytes(
        self, decompressor: EndlessZstdDecompressor, f: BufferedIOBase, output_size: int
    ) -> bytes:
        while len(self._decompress_buffer) < output_size:
            if decompressor.needs_input:
                f_data = f.read(1024**2)

                if not f_data:
                    break
            else:
                f_data = b""

            self._decompress_buffer += decompressor.decompress(f_data, max_length=output_size)

        out = self._decompress_buffer[:output_size]
        self._decompress_buffer = self._decompress_buffer[output_size:]

        return out

    def _snapshot_message_from_stream(
        self, decompressor: EndlessZstdDecompressor, f: BufferedIOBase
    ) -> Optional[SnapshotMessage]:
        packed_metadata = self._decompress_bytes(decompressor, f, 24)
        if not packed_metadata:
            return None
        elif len(packed_metadata) < 24:
            raise ValueError("Failed to read metadata from stream")

        time, market_value, feedcode_size, bids_size, asks_size = struct.unpack(
            "QIIII", packed_metadata
        )

        feedcode_data = self._decompress_bytes(decompressor, f, feedcode_size)
        if len(feedcode_data) != feedcode_size:
            raise ValueError("Failed to read feedcode from stream")

        bids_bytes = self._decompress_bytes(decompressor, f, bids_size)
        if len(bids_bytes) != bids_size:
            raise ValueError("Failed to read bids from stream")
        bids = np.frombuffer(bids_bytes)

        asks_bytes = self._decompress_bytes(decompressor, f, asks_size)
        if len(asks_bytes) != asks_size:
            raise ValueError("Failed to read asks from stream")
        asks = np.frombuffer(asks_bytes)

        return SnapshotMessage(
            time=time,
            feedcode=feedcode_data.decode(),
            market=Market(market_value),
            bids=bids.reshape((-1, 2)).tolist(),
            asks=asks.reshape((-1, 2)).tolist(),
        )

    def stream_updates(
        self, asset: str, since: datetime, until: Optional[datetime]
    ) -> Generator[SnapshotMessage, None, None]:
        asset_path = os.path.join(self._resource_path, asset)
        if not os.path.exists(asset_path):
            raise ValueError(f"No directory for `{asset}` found in resource path")

        if not until:
            until = datetime.today()

        for i in range((until - since).days):
            cur = since + timedelta(days=i)
            cur_file_name = cur.strftime("%m_%d_%Y")
            cur_path = os.path.join(asset_path, cur_file_name)

            if not os.path.exists(cur_path):
                raise ValueError(f"Expected file '{cur_path}' does not exist")

        decompressor = EndlessZstdDecompressor()

        for i in range((until - since).days):
            cur = since + timedelta(days=i)
            cur_file_name = cur.strftime("%m_%d_%Y")
            cur_path = os.path.join(asset_path, cur_file_name)

            with open(cur_path, "rb") as f:
                while True:
                    snapshot = self._snapshot_message_from_stream(decompressor, f)
                    if not snapshot:
                        break

                    yield snapshot
