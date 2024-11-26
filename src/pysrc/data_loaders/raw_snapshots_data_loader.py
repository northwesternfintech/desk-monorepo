from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from pysrc.adapters.kraken.asset_mappings import asset_to_kraken
from pysrc.adapters.messages import SnapshotMessage
from pysrc.data_handlers.kraken.historical.snapshots_data_handler import (
    SnapshotsDataHandler,
)
from pysrc.data_loaders.base_data_loader import BaseDataLoader
from pysrc.util.exceptions import DIE
from pysrc.util.types import Asset, Market


class RawSnapshotsDataLoader(BaseDataLoader):
    def __init__(
        self,
        resource_path: Path,
        asset: Asset,
        market: Market,
        since: date,
        until: date,
    ) -> None:
        self._feedcode = asset_to_kraken(asset, market)
        self._resource_path = resource_path
        self._asset_resource_path = resource_path / "snapshots" / self._feedcode
        if not self._asset_resource_path.exists():
            DIE(
                f"Directory for asset snapshots data '{self._asset_resource_path}' doesn't exist"
            )

        self._asset = asset
        self._market = market
        self._handler = SnapshotsDataHandler()

        self._since = since
        self._until = until
        if self._since >= self._until:
            DIE(
                f"Dates since ({self._since.strftime("%m_%d_%Y")}) equal to or later than until ({self._until.strftime("%m_%d_%Y")})"
            )
        self._cur_date = since
        self._cur_path = self._asset_resource_path / self._cur_date.strftime(
            "%m_%d_%Y.bin"
        )
        if not self._cur_path.exists():
            DIE(f"Expected file '{self._cur_path}' doesn't exist")
        self._cur_generator = self._handler.stream_read(self._cur_path)

    def get_data(self, since: date, until: date) -> list[SnapshotMessage]:
        if since >= until:
            DIE(
                f"Dates since ({since.strftime("%m_%d_%Y")}) equal to or later than until ({until.strftime("%m_%d_%Y")})"
            )
        file_paths = []
        snapshots = []

        for i in range((until - since).days):
            cur = since + timedelta(days=i)
            cur_file_name = cur.strftime("%m_%d_%Y.bin")
            cur_path = self._asset_resource_path / cur_file_name
            if not cur_path.exists():
                DIE(f"Expected file '{cur_path}' doesn't exist")
            file_paths.append(cur_path)

        for file_path in file_paths:
            snapshots.extend(self._handler.read(file_path))

        return snapshots

    def next(self) -> Optional[SnapshotMessage]:
        try:
            return next(self._cur_generator)
        except StopIteration:
            self._cur_date += timedelta(days=1)
            self._cur_path = self._asset_resource_path / self._cur_date.strftime(
                "%m_%d_%Y.bin"
            )
            if self._cur_date >= self._until:
                return None
            if not self._cur_path.exists():
                return None
            self._cur_generator = self._handler.stream_read(self._cur_path)
            return next(self._cur_generator)
