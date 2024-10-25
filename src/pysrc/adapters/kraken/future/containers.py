from pysrc.util import exceptions
from typing import Any, List, Optional


def safe_at(list: List[Any], idx: int) -> Optional[Any]:
    if (idx < 0 and abs(idx) > len(list)) or (idx >= 0 and idx >= len(list)):
        return exceptions.DIE("Safe at failed due to index out of bounds")
    return list[idx]


def get_single(list: List[Any]) -> Optional[Any]:
    if len(list) != 1:
        return exceptions.DIE(
            "Get single failed due to list not having exactly one element"
        )
    return list[0]
