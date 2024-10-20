from pysrc.util.types import Asset
from pathlib import Path

def get_lasso_model_filename(asset: Asset) -> str:
    return(str(asset.name) + "_lasso.pkl")

def check_lasso_models(directory_path: Path, assets: list[Asset]) -> bool:
    for asset in assets:
        model_filename = get_lasso_model_filename(asset)
        model_path = directory_path.joinpath(model_filename)
        if not model_path.exists():
            return False
    return True



# from pysrc.test.helpers import get_resources_path
# resource_path = get_resources_path(Path(__file__).resolve())
# print(resource_path)