from pysrc.adapters.kraken.historical.historical_data_client import HistoricalDataClient
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
            res.extend(hist_client.get_trades(self.coin, date, ""))
        return res

    def calculate_features(self) -> dict[str, list[float]]:
        trades = self._get_data_daterange(self.start, self.end)
        # ^ this returns a list[TradeMessage], but on_tick expects dict[str, TradeMessage]
        # What is key?
        snapshots = {}
        # ^ how to get snapshots?
        generator_client = BaseFeatureGenerator()
        feature_dict = generator_client.on_tick(snapshots, trades)
        return feature_dict[self.asset]

    # Suppose that returns is passed to evaluate_features
    def evaluate_features(self, target: list[float]):
        calc_features = self.calculate_features()
        input_matrix = []
        for feature in self.features:
            input_matrix.append(calc_features[feature])
        input_matrix.append(target)
        return np.corrocoef(input_matrix)
