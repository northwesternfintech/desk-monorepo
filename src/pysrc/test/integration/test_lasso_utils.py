from pysrc.util.types import Asset
from pysrc.util.lasso_utils import check_lasso_models
from pysrc.test.helpers import get_resources_path
from pathlib import Path


def test_check_lasso_models() -> None:
    resource_path = get_resources_path(str(Path(__file__).resolve()))
    assert check_lasso_models(resource_path, [])
    assert check_lasso_models(resource_path, [Asset.BTC])
    assert check_lasso_models(resource_path, [Asset.BTC, Asset.DOGE, Asset.ETH])
    assert not check_lasso_models(resource_path, [Asset.ADA])
    assert not check_lasso_models(resource_path, [Asset.ADA, Asset.AVAX, Asset.SHIB])
    assert not check_lasso_models(resource_path, [Asset.BTC, Asset.ADA])
