from enum import Enum
import pytest
from pysrc.util.enum_conversions import enum_to_string, string_to_enum
from typing import TypeVar


class ExampleEnum(Enum):
    VALUE_ONE = 1
    VALUE_TWO = 2
    VALUE_THREE = 3


def test_enum_to_string() -> None:
    assert enum_to_string(ExampleEnum.VALUE_ONE) == "VALUE_ONE"
    assert enum_to_string(ExampleEnum.VALUE_TWO) == "VALUE_TWO"
    assert enum_to_string(ExampleEnum.VALUE_THREE) == "VALUE_THREE"


def test_string_to_enum() -> None:
    assert string_to_enum(ExampleEnum, "VALUE_ONE") == ExampleEnum.VALUE_ONE
    assert string_to_enum(ExampleEnum, "VALUE_TWO") == ExampleEnum.VALUE_TWO
    assert string_to_enum(ExampleEnum, "VALUE_THREE") == ExampleEnum.VALUE_THREE


def test_string_to_enum_case_insensitivity() -> None:
    assert string_to_enum(ExampleEnum, "value_one") == ExampleEnum.VALUE_ONE
    assert string_to_enum(ExampleEnum, "VaLuE_TwO") == ExampleEnum.VALUE_TWO


def test_string_to_enum_invalid_value() -> None:
    with pytest.raises(
        ValueError, match="'INVALID' is not a valid member of ExampleEnum"
    ):
        string_to_enum(ExampleEnum, "INVALID")
