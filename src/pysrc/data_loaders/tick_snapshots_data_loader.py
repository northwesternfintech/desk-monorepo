from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from pysrc.adapters.messages import SnapshotMessage
from pysrc.data_loaders.base_data_loader import BaseDataLoader
from pysrc.data_loaders.raw_snapshots_data_loader import RawSnapshotsDataLoader
from pysrc.util.types import Asset, Market


class TickSnapshotsDataLoader(BaseDataLoader):
    def __init__(
        self,
        resource_path: Path,
        asset: Asset,
        market: Market,
        since: date,
        until: date,
    ) -> None:
        self._raw_loader = RawSnapshotsDataLoader(
            resource_path=resource_path,
            asset=asset,
            market=market,
            since=since,
            until=until,
        )
        self._start_timestamp = self._date_to_timestamp(self._raw_loader._since)
        self._end_timestamp = self._date_to_timestamp(self._raw_loader._until)
        self._cur_timestamp = self._date_to_timestamp(self._raw_loader._since)
        self._cur_snapshot = SnapshotMessage(
            time=self._cur_timestamp,
            feedcode=self._raw_loader._feedcode,
            bids=[],
            asks=[],
            market=self._raw_loader._market,
        )
        self._next_shapsnot: Optional[SnapshotMessage] = None

    def _date_to_timestamp(self, d: date) -> int:
        dt = datetime.combine(d, datetime.min.time())
        return int(dt.replace(tzinfo=timezone.utc).timestamp())

    def get_data(self, since: date, until: date) -> list[SnapshotMessage]:
        return self._raw_loader.get_data(since, until)

    def next(self) -> Optional[SnapshotMessage]:
        if self._cur_timestamp >= self._end_timestamp:
            return None

        if self._next_shapsnot is not None:
            if self._next_shapsnot.time < self._cur_timestamp:
                raise ValueError(
                    "Unexpected invariance breach: snapshot time should be monotonically increasing"
                )
            elif self._next_shapsnot.time > self._cur_timestamp:
                self._cur_timestamp += 1
                return self._cur_snapshot
            else:
                self._cur_snapshot = self._next_shapsnot
                self._next_shapsnot = None

        while True:
            new_snapshot = self._raw_loader.next()
            if new_snapshot is None:
                break
            if new_snapshot.time < self._cur_timestamp:
                raise ValueError(
                    "Unexpected invariance breach: snapshot time should be monotonically increasing"
                )
            elif new_snapshot.time == self._cur_timestamp:
                self._cur_snapshot = new_snapshot
            else:
                self._next_shapsnot = new_snapshot
                break

        self._cur_timestamp += 1
        return self._cur_snapshot
