import logging
from typing import NoReturn

LOGGER = logging.getLogger(__name__)


def DIE(error_msg: str) -> NoReturn:
    LOGGER.exception(error_msg)
    raise AssertionError(error_msg)


def prod_assert(condition: bool, error_msg: str) -> None:
    if not condition:
        DIE(error_msg)
