from datetime import datetime
from pathlib import Path

import numpy as np

from pysrc.adapters.kraken.asset_mappings import asset_to_kraken
from pysrc.data_loaders.tick_snapshots_data_loader import TickSnapshotsDataLoader
from pysrc.data_loaders.tick_trades_data_loader import TickTradesDataLoader
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

    def calculate_features(
        self,
        generator_client: BaseFeatureGenerator,
    ) -> dict[str, list[float]]:
        trades_client = TickTradesDataLoader(
            self._resource_path, self._asset, self._market, self._start, self._end
        )
        snapshots_client = TickSnapshotsDataLoader(
            self._resource_path, self._asset, self._market, self._start, self._end
        )

        feature_dict: dict[str, list[float]] = {}
        for feature in self._features:
            feature_dict[feature] = []

        asset_str = asset_to_kraken(self._asset, self._market)

        while (trade := trades_client.next()) is not None and (
            snapshot := snapshots_client.next()
        ) is not None:
            calc_features = generator_client.on_tick(
                {asset_str: snapshot}, {asset_str: trade}
            )
            for i in range(len(self._features)):
                feature = self._features[i]
                feature_dict[feature].append(calc_features[self._asset]["features"][i])
        return feature_dict

    def evaluate_features(
        self, calc_features: dict[str, list[float]], target: list[float]
    ) -> np.ndarray:
        input_matrix = []
        for feature in self._features:
            input_matrix.append(calc_features[feature])
        return np.corrcoef(input_matrix, target)
