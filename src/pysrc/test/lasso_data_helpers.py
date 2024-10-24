import numpy as np
from pathlib import Path
from pysrc.util.types import Asset
from pysrc.util.lasso_utils import asset_to_model_filename
from pysrc.util.pickle_utils import load_pickle, store_pickle
from pysrc.util.enum_conversions import enum_to_string

from sklearn.linear_model import Lasso
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_regression


def generate_sample_lasso_model_and_data(**kwargs: float) -> tuple:
    n_samples = kwargs.get("n_samples", 100)
    n_features = kwargs.get("n_features", 20)
    noise = kwargs.get("noise", 0.1)
    random_state = kwargs.get("random_state", 42)
    test_size = kwargs.get("test_size", 0.2)
    alpha = kwargs.get("alpha", 0.5)

    X, y = make_regression(
        n_samples=n_samples,
        n_features=n_features,
        noise=noise,
        random_state=random_state,
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    lasso_model = Lasso(alpha=alpha)
    lasso_model.fit(X_train, y_train)
    return X_train, X_test, y_train, y_test, lasso_model


def generate_lasso_integration_testing_data(directory_path: Path) -> None:
    assets = [Asset.BTC, Asset.DOGE, Asset.ETH]

    kwargs1 = dict(
        n_samples=10000,
        n_features=20,
        noise=0.1,
        random_state=42,
        test_size=0.2,
        alpha=1,
    )

    kwargs2 = dict(
        n_samples=10000,
        n_features=100,
        noise=1,
        random_state=42,
        test_size=0.2,
        alpha=2,
    )

    kwargs3 = dict(
        n_samples=10000,
        n_features=500,
        noise=10,
        random_state=42,
        test_size=0.2,
        alpha=2,
    )

    kwargs_lst = [kwargs1, kwargs2, kwargs3]

    for i, asset in enumerate(assets):
        asset_str = enum_to_string(asset)
        X_train, X_test, y_train, y_test, lasso_model = (
            generate_sample_lasso_model_and_data(**kwargs_lst[i])
        )
        test_data = np.hstack([X_test, y_test.reshape(-1, 1)])
        store_pickle(test_data, directory_path.joinpath(f"{asset_str}_test_data.pkl"))
        store_pickle(
            lasso_model, directory_path.joinpath(asset_to_model_filename(asset))
        )


def test_lasso_integration_testing_data(directory_path: Path) -> None:
    assets = [Asset.BTC, Asset.DOGE, Asset.ETH]
    for asset in assets:
        asset_str = enum_to_string(asset)
        test_data = load_pickle(directory_path.joinpath(f"{asset_str}_test_data.pkl"))
        X_test = test_data[:, :-1]
        y_test = test_data[:, -1]
        lasso_model = load_pickle(
            directory_path.joinpath(asset_to_model_filename(asset))
        )
        score = lasso_model.score(X_test, y_test)
        print(f"{asset} model R-squared score: {score}")

    print(type(X_test))
    print(X_test.shape, y_test.shape, test_data.shape)


# if __name__ == '__main__':
#     directory_path = Path(__file__).parent.joinpath('integration/resources')
#     generate_lasso_integration_testing_data(directory_path)
#     test_lasso_integration_testing_data(directory_path)
