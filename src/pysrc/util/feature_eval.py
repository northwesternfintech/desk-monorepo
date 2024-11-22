import itertools
import os
from datetime import datetime
from pathlib import Path
from typing import Iterable

import numpy as np
from dateutil.rrule import DAILY, rrule

from pysrc.adapters.kraken.asset_mappings import kraken_to_asset
from pysrc.adapters.messages import SnapshotMessage, TradeMessage
from pysrc.data_handlers.kraken.historical.snapshots_data_handler import (
    SnapshotsDataHandler,
)
from pysrc.data_handlers.kraken.historical.trades_data_handler import TradesDataHandler
from pysrc.signal.base_feature_generator import BaseFeatureGenerator


class Evaluator:
    def __init__(self, features: list[str], asset: str, start: datetime, end: datetime):
        self.features = features
        self.asset = asset
        self.start = start
        self.end = end
        pass

    def _get_data_daterange(
        self,
        start: datetime,
        end: datetime,
        trades_resource_path: str,
        snapshots_resource_path: str,
    ) -> Iterable[tuple[TradeMessage, SnapshotMessage]]:
        trades_client = TradesDataHandler()
        snapshots_client = SnapshotsDataHandler()

        trade_generators = []
        snapshot_generators = []

        for date in rrule(DAILY, dtstart=start, until=end):
            trades_filepath = os.path.join(
                trades_resource_path, self.asset, date.strftime("%m_%d_%Y") + ".bin"
            )
            trade_gen = trades_client.stream_read(Path(trades_filepath))

            snapshots_filepath = os.path.join(
                snapshots_resource_path, self.asset, date.strftime("%m_%d_%Y") + ".bin"
            )
            snapshot_gen = snapshots_client.stream_read(Path(snapshots_filepath))

            trade_generators.append(trade_gen)
            snapshot_generators.append(snapshot_gen)

        combined_trades_gen = itertools.chain.from_iterable(trade_generators)
        combined_snapshots_gen = itertools.chain.from_iterable(snapshot_generators)
        return zip(combined_trades_gen, combined_snapshots_gen)

    def calculate_features(
        self,
        generator_client: BaseFeatureGenerator,
        trades_filepath: str,
        snapshots_filepath: str,
    ) -> dict[str, list[float]]:
        data = self._get_data_daterange(
            self.start, self.end, trades_filepath, snapshots_filepath
        )

        feature_dict: dict[str, list[float]] = {}
        for feature in self.features:
            feature_dict[feature] = []

        for trade, snapshot in data:
            print("huh")
            print(trade)
            print(snapshot)
            calc_features = generator_client.on_tick(
                {self.asset: snapshot}, {self.asset: [trade]}
            )
            print(calc_features)
            for feature in self.features:
                asset_enum = kraken_to_asset(self.asset)
                feature_dict[feature].extend(calc_features[asset_enum][feature])
                print(id(feature_dict[feature]))
        return feature_dict

    # Suppose that returns is passed to evaluate_features
    def evaluate_features(
        self, calc_features: dict[str, list[float]], target: list[float]
    ) -> np.ndarray:
        input_matrix = []
        for feature in self.features:
            input_matrix.append(calc_features[feature])
        return np.corrcoef(input_matrix, target)
