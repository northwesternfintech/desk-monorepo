from pysrc.util.exceptions import DIE
from collections.abc import Sequence


def safe_at[T](lst: Sequence[T], idx: int) -> T:
    if (idx < 0 and abs(idx) > len(lst)) or (idx >= 0 and idx >= len(lst)):
        return DIE("Safe at failed due to index out of bounds")
    return lst[idx]


def get_single[T](singleList: Sequence[T]) -> T:
    if len(singleList) != 1:
        return DIE("Get single failed due to list not having exactly one element")
    return singleList[0]
