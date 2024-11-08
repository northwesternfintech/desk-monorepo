from typing import Any, Optional


class Evaluator:

    def __init__(self, features, coin, start, end):
        self.features = features
        self.coin = coin
        self.start = start
        self.end = end
        pass

    def _get_data_daterange(start, end):
        # hist_client = HistoricalDataClient()
        # res = []
        # for date in range(start, end):
        #   res.append(hist_client.get_trades(self.coin, date, resource_path...?))
        # return res
        pass

    def calculate_features(self):
        # trades = self._get_data_daterange(self.start, self.end)
        # generator_client = BaseFeatureGenerator()
        # feature_dict = generator_client.on_tick(..., trades)
        # ^ how to get snapshots? HistoricalDataClient() only has methods for trades
        pass

    def evaluate_features(self, target):
        # calc_features = self.calculate_features()
        # assess against a target...?
        pass

