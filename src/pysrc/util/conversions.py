from enum import Enum
from typing import Type, TypeVar

T = TypeVar("T", bound=Enum)


def enum_to_string(enum_val: T) -> str:
    return enum_val.name


def string_to_enum(enum_class: Type[T], value: str) -> T:
    try:
        return enum_class[value.upper()]
    except KeyError:
        raise ValueError(f"'{value}' is not a valid member of {enum_class.__name__}")
