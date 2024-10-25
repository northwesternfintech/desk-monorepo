from pysrc.adapters.kraken.future.containers import safe_at, get_single
from pysrc.util import exceptions
import pytest


def test_safe_at() -> None:
    testList = [1, 2, 3]
    assert safe_at(testList, 0) == 1
    assert safe_at(testList, 1) == 2
    assert safe_at(testList, 2) == 3
    assert safe_at(testList, -1) == 3
    assert safe_at(testList, -2) == 2
    assert safe_at(testList, -3) == 1

    with pytest.raises(
        AssertionError, match="Safe at failed due to index out of bounds"
    ):
        safe_at(testList, 3)

    with pytest.raises(
        AssertionError, match="Safe at failed due to index out of bounds"
    ):
        safe_at(testList, -4)

def test_get_single() -> None:
    testSingleFailList: list[int] = []
    testSingleFailList2 = [1, 2]
    singleList = [1]

    assert get_single(singleList) == 1

    with pytest.raises(
        AssertionError,
        match="Get single failed due to list not having exactly one element",
    ):
        get_single(testSingleFailList)

    with pytest.raises(
        AssertionError,
        match="Get single failed due to list not having exactly one element",
    ):
        get_single(testSingleFailList2)
