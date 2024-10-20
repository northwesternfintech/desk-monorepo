from pysrc.util.types import Asset
from pysrc.util.enum_conversions import enum_to_string
from pathlib import Path

def get_lasso_model_filename(asset: Asset) -> str:
    return(enum_to_string(asset) + "_lasso.pkl")

def check_lasso_models(directory_path: Path, assets: list[Asset]) -> bool:
    for asset in assets:
        model_filename = get_lasso_model_filename(asset)
        model_path = directory_path.joinpath(model_filename)
        if not model_path.exists():
            return False
    return True
