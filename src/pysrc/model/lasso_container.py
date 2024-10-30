from pathlib import Path
from pysrc.util.types import Asset
from pysrc.util.lasso_utils import asset_to_model_filename, search_model_in_directory
from pysrc.util.pickle_utils import load_pickle


class LassoContainer:
    def __init__(self, resource_path: Path, assets: list[Asset]) -> None:
        self.resource_path = resource_path
        self.models = {}
        for asset in assets:
            if not search_model_in_directory(resource_path, [asset]):
                raise AssertionError(
                    "LassoContainer initialized without an instantiated model for one or more assets"
                )
            model = load_pickle(resource_path.joinpath(asset_to_model_filename(asset)))
            self.models[asset] = model

    def predict(self, features: dict[Asset, list[float]]) -> dict[Asset, float]:
        assets = list(features.keys())
        if not search_model_in_directory(self.resource_path, assets):
            raise AssertionError(
                "Inference attempted without an instantiated model for one or more assets"
            )
        predictions = {}
        for asset, inputs in features.items():
            predictions[asset] = self.models[asset].predict([inputs]).item()
        return predictions
