from pysrc.util.types import Asset
from pysrc.util.lasso_utils import search_model_in_directory
from pysrc.test.helpers import get_resources_path


def test_check_lasso_models_positive() -> None:
    resource_path = get_resources_path(__file__)
    assert not search_model_in_directory(resource_path, [Asset.ADA])
    assert not search_model_in_directory(
        resource_path, [Asset.ADA, Asset.AVAX, Asset.SHIB]
    )
    assert not search_model_in_directory(resource_path, [Asset.BTC, Asset.ADA])


def test_check_lasso_models_negative() -> None:
    resource_path = get_resources_path(__file__)
    assert not search_model_in_directory(resource_path, [Asset.ADA])
    assert not search_model_in_directory(
        resource_path, [Asset.ADA, Asset.AVAX, Asset.SHIB]
    )
    assert not search_model_in_directory(resource_path, [Asset.BTC, Asset.ADA])
