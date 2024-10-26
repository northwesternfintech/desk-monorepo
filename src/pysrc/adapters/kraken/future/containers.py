from pysrc.util.exceptions import DIE
from collections.abc import Sequence
from typing import Any


def safe_at(list: Sequence[Any], idx: int) -> Any:
    if (idx < 0 and abs(idx) > len(list)) or (idx >= 0 and idx >= len(list)):
        return DIE("Safe at failed due to index out of bounds")
    return list[idx]


def get_single(list: Sequence[Any]) -> Any:
    if len(list) != 1:
        return DIE("Get single failed due to list not having exactly one element")
    return list[0]
