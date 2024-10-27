import numpy as np
from pathlib import Path
from pysrc.util.types import Asset
from pysrc.util.enum_conversions import enum_to_string
from pysrc.util.pickle_utils import load_pickle
from pysrc.model.lasso_container import LassoContainer
from pysrc.test.helpers import get_resources_path
import pytest

resource_path = get_resources_path(__file__)


def test_lasso_container_failed_initialization() -> None:
    error_msg = "LassoContainer initialized without an instantiated model for one ore more assets"

    with pytest.raises(AssertionError) as excinfo:
        LassoContainer(resource_path, [Asset.ADA])
    assert str(excinfo.value) == error_msg

    with pytest.raises(AssertionError) as excinfo:
        LassoContainer(resource_path, [Asset.BTC, Asset.ETH, Asset.DOGE, Asset.ADA])
    assert str(excinfo.value) == error_msg


def test_lasso_container_successful_initialization() -> None:
    LassoContainer(resource_path, [])
    LassoContainer(resource_path, [Asset.BTC])
    LassoContainer(resource_path, [Asset.ETH, Asset.DOGE])
    LassoContainer(resource_path, [Asset.BTC, Asset.ETH, Asset.DOGE])


def test_lasso_container_failed_inference() -> None:
    error_msg = (
        "Inference attempted without an instantiated model for one or more assets"
    )
    container = LassoContainer(resource_path, [Asset.BTC, Asset.ETH, Asset.DOGE])

    with pytest.raises(AssertionError) as excinfo:
        container.predict({Asset.ADA: [1, 1, 1]})
    assert str(excinfo.value) == error_msg

    with pytest.raises(AssertionError) as excinfo:
        container.predict({Asset.BTC: [1], Asset.ETH: [1], Asset.ADA: [1]})
    assert str(excinfo.value) == error_msg


def test_lasso_container_successful_inference() -> None:
    assets = [Asset.BTC, Asset.DOGE, Asset.ETH]
    container = LassoContainer(resource_path, assets)
    all_features = dict()
    all_targets = dict()

    for asset in assets:
        asset_str = enum_to_string(asset)
        test_data = load_pickle(resource_path.joinpath(f"{asset_str}_test_data.pkl"))
        X_test = test_data[:, :-1]
        y_test = test_data[:, -1]
        all_features[asset] = X_test
        all_targets[asset] = y_test

    num_samples = [data.shape[0] for data in all_features.values()]
    assert all(x == num_samples[0] for x in num_samples)

    all_predictions: dict = {asset: [] for asset in assets}
    for i in range(0, num_samples[0]):
        features = {asset: all_features[asset][i, :] for asset in assets}
        predictions = container.predict(features)
        for asset in assets:
            all_predictions[asset].append(predictions[asset])

    for asset in assets:
        asset_predictions = all_predictions[asset]
        asset_targets = all_targets[asset]
        corr = np.corrcoef(asset_predictions, asset_targets)[0, 1]
        assert corr >= 0.995
