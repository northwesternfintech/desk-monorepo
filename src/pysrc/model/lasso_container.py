from abc import ABC
from pathlib import Path
from pysrc.util.types import Asset
from pysrc.util.lasso_utils import asset_to_model_filename, search_model_in_directory
from pysrc.util.pickle_utils import load_pickle


class LassoContainer(ABC):
    """
    Class that maintains a mapping from the Assets to sklearn Lasso regressors
    """

    def __init__(self, resource_path: Path, assets: list[Asset]) -> None:
        """
        Initialize the Lasso container

        Parameters
        ----------
        resource_path
            Path of the directory containing stored Lasso model pickle files
        assets
            List of assets to initialize model on. Each asset should have a corresponding Lasso model stored in resource_path

        Raises
        ------
        AssertionError if one or more assets passed in don't have a Lasso model stored in resource_path

        """
        self.resource_path = resource_path
        self.models = {}
        for asset in assets:
            if not search_model_in_directory(resource_path, [asset]):
                raise AssertionError(
                    "LassoContainer initialized without an instantiated model for one ore more assets"
                )
            model = load_pickle(resource_path.joinpath(asset_to_model_filename(asset)))
            self.models[asset] = model

    def predict(self, features: dict[Asset, list[float]]) -> dict[Asset, float]:
        """
        Perform inference on a set of assets using their respective models

        Parameters
        ----------
        features
            Key is the asset
            Value is feature data in one sample of the asset

        Raises
        ------
        AssertionError if one or more assets passed in don't have an instantiated model

        Returns
        -------
        dict[Asset, float]
            Predictions for the target using the input features and stored model. One prediction per asset.
        """
        assets = list(features.keys())
        if not search_model_in_directory(self.resource_path, assets):
            raise AssertionError(
                "Inference attempted without an instantiated model for one or more assets"
            )
        predictions = {}
        for asset, inputs in features.items():
            predictions[asset] = self.models[asset].predict([inputs]).item()
        return predictions
