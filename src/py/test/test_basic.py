import pytest
from src.py.util.hello_test_function import hello_world

def test_basic() -> None:
    assert 4 == 4

def test_hello_world() -> None:
    assert hello_world() == "Hello, World!"
