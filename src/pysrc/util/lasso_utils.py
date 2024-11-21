from pathlib import Path

from pysrc.util.enum_conversions import enum_to_string
from pysrc.util.types import Asset


def asset_to_model_filename(asset: Asset) -> str:
    return f"{enum_to_string(asset)}_lasso.pkl"


def search_model_in_directory(directory_path: Path, assets: list[Asset]) -> bool:
    for asset in assets:
        model_filename = asset_to_model_filename(asset)
        model_path = directory_path.joinpath(model_filename)
        if not model_path.exists():
            return False
    return True
