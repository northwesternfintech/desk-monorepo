from pysrc.util.types import Asset
from pysrc.util.lasso_utils import get_lasso_model_filename
from pysrc.util.enum_conversions import enum_to_string


def test_get_lasso_model_filename() -> None:
    for asset in Asset:
        model_filename = get_lasso_model_filename(asset)
        assert model_filename == f"{enum_to_string(asset)}_lasso.pkl"
