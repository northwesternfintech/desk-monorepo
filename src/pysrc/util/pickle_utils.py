import pickle
from pathlib import Path
from typing import Any


def store_pickle(data: Any, path: Path) -> None:
    with path.open("wb") as f:
        pickle.dump(data, f)


def load_pickle(path: Path) -> Any:
    with path.open("rb") as f:
        return pickle.load(f)
