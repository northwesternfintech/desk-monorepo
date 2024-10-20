from pysrc.util.types import Asset
from pysrc.util.lasso_utils import get_lasso_model_filename


def test_get_lasso_model_filename() -> None:
    for asset in Asset:
        model_filename = get_lasso_model_filename(asset)
        assert model_filename == f"{asset.name}_lasso.pkl"
