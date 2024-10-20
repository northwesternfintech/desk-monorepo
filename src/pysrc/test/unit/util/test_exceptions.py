from pysrc.util.exceptions import DIE, prod_assert

import pytest


def test_die_with_message() -> None:
    with pytest.raises(AssertionError) as excinfo:
        DIE("assertion failure message")
        assert str(excinfo.value) == "assertion failure message"


def test_prod_assert_pass() -> None:
    prod_assert(True, "error")


def test_prod_assert_fail() -> None:
    with pytest.raises(AssertionError) as excinfo:
        prod_assert(False, "test_error_msg")
    assert str(excinfo.value) == "test_error_msg"
