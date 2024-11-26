import itertools
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

import numpy as np

from pysrc.adapters.kraken.asset_mappings import asset_to_kraken
from pysrc.adapters.messages import SnapshotMessage, TradeMessage
from pysrc.data_handlers.kraken.historical.snapshots_data_handler import (
    SnapshotsDataHandler,
)
from pysrc.data_handlers.kraken.historical.trades_data_handler import TradesDataHandler
from pysrc.signal.base_feature_generator import BaseFeatureGenerator
from pysrc.util.types import Asset, Market


class Evaluator:
    def __init__(
        self,
        features: list[str],
        asset: Asset,
        market: Market,
        start: datetime,
        end: datetime,
        resource_path: Path,
    ):
        self._features = features
        self._asset = asset
        self._start = start
        self._end = end
        self._market = market
        self._resource_path = resource_path

    def _get_data_daterange(
        self,
        start: datetime,
        end: datetime,
    ) -> Iterable[tuple[TradeMessage, SnapshotMessage]]:
        trades_client = TradesDataHandler()
        snapshots_client = SnapshotsDataHandler()

        trade_generators = []
        snapshot_generators = []
        delta_time = timedelta(days=1)
        asset_str = asset_to_kraken(self._asset, self._market)

        while start <= end:
            trades_filepath = (
                self._resource_path
                / "trades"
                / asset_str
                / (start.strftime("%m_%d_%Y") + ".bin")
            )
            trade_gen = trades_client.stream_read(trades_filepath)

            snapshots_filepath = (
                self._resource_path
                / "snapshots"
                / asset_str
                / (start.strftime("%m_%d_%Y") + ".bin")
            )
            snapshot_gen = snapshots_client.stream_read(snapshots_filepath)

            trade_generators.append(trade_gen)
            snapshot_generators.append(snapshot_gen)
            start += delta_time

        combined_trades_gen = itertools.chain.from_iterable(trade_generators)
        combined_snapshots_gen = itertools.chain.from_iterable(snapshot_generators)
        return zip(combined_trades_gen, combined_snapshots_gen)

    def calculate_features(
        self,
        generator_client: BaseFeatureGenerator,
    ) -> dict[str, list[float]]:
        data = self._get_data_daterange(self._start, self._end)

        feature_dict: dict[str, list[float]] = {}
        for feature in self._features:
            feature_dict[feature] = []

        asset_str = asset_to_kraken(self._asset, self._market)

        for trade, snapshot in data:
            calc_features = generator_client.on_tick(
                {asset_str: snapshot}, {asset_str: [trade]}
            )
            for feature in self._features:
                feature_dict[feature].extend(calc_features[self._asset][feature])
        return feature_dict

    def evaluate_features(
        self, calc_features: dict[str, list[float]], target: list[float]
    ) -> np.ndarray:
        input_matrix = []
        for feature in self._features:
            input_matrix.append(calc_features[feature])
        return np.corrcoef(input_matrix, target)
