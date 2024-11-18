from pysrc.adapters.kraken.historical.historical_data_client import (
    HistoricalUpdatesDataClient,
    HistoricalDataClient
)
from datetime import datetime
from dateutil.rrule import rrule, DAILY
from pysrc.util.types import TradeMessage, Asset
from pysrc.signal.base_feature_generator import BaseFeatureGenerator
import numpy as np


class Evaluator:

    def __init__(self, features: list[str], asset: Asset, start: datetime, end: datetime):
        self.features = features
        self.asset = asset
        self.start = start
        self.end = end
        pass

    def _get_data_daterange(self, start: datetime, end: datetime) -> list[TradeMessage]:
        hist_client = HistoricalDataClient()
        res = []
        for date in rrule(DAILY, dtstart=start, until=end):
            res.extend(hist_client.get_trades(self.asset, date, ""))

        update_client = HistoricalUpdatesDataClient()
        generator = update_client.stream_updates(self.asset, start, end)
        return zip(res, generator)

    def calculate_features(self) -> dict[str, list[float]]:
        data = self._get_data_daterange(self.start, self.end)
        generator_client = BaseFeatureGenerator()
        feature_dict = dict.fromkeys(self.features, [])
        for trade, snapshot in data:
            features = generator_client.on_tick(snapshot, trade)
            for feature in self.features:
                feature_dict[feature].extend(features[self.asset][feature])
        return feature_dict

    # Suppose that returns is passed to evaluate_features
    def evaluate_features(self, target: list[float]):
        calc_features = self.calculate_features()
        input_matrix = []
        for feature in self.features:
            input_matrix.append(calc_features[feature])
        input_matrix.append(target)
        return np.corrcoef(input_matrix)
