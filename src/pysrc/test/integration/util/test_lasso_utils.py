from pathlib import Path
from pysrc.util.types import Asset
from pysrc.util.lasso_utils import search_model_in_directory
from pysrc.test.helpers import get_resources_path

resource_path = get_resources_path(str(Path(__file__).parent))


def test_check_lasso_models_positive() -> None:
    assert search_model_in_directory(resource_path, [Asset.BTC])
    assert search_model_in_directory(resource_path, [Asset.BTC, Asset.DOGE, Asset.ETH])
    assert search_model_in_directory(resource_path, [Asset.BTC, Asset.ETH])


def test_check_lasso_models_negative() -> None:
    assert not search_model_in_directory(resource_path, [Asset.ADA])
    assert not search_model_in_directory(
        resource_path, [Asset.ADA, Asset.AVAX, Asset.SHIB]
    )
    assert not search_model_in_directory(resource_path, [Asset.BTC, Asset.ADA])
