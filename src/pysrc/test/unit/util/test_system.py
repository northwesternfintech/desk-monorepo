import pytest

from pysrc.util.system import (
    get_current_server,
    get_current_user,
    _get_current_server_hostname,
    _hostname_to_enum,
)
from pysrc.util.types import Server


def test_current_hostname() -> None:
    hostname = _get_current_server_hostname()
    assert type(hostname) is str


def test_hostname_enum_conversion() -> None:
    assert type(_hostname_to_enum("john")) is Server
    assert _hostname_to_enum("black") == Server.BLACK
    assert _hostname_to_enum("scholes") == Server.SCHOLES
    assert _hostname_to_enum("john") == Server.FOREIGN


def test_current_server() -> None:
    assert type(get_current_server()) is Server


def test_current_user() -> None:
    assert type(get_current_user()) is str
