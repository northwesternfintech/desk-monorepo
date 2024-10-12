from pysrc.exec.action import Action
from pysrc.test.unit.helpers import get_test_instrument
from pysrc.util.types import OrderSide, LiquidityType

import pytest


def test_action_ctor_taker() -> None:
    Action(get_test_instrument(), OrderSide.BID, LiquidityType.TAKER, 15, 22.1)
    Action(get_test_instrument(), OrderSide.BID, LiquidityType.TAKER, 15, None)


def test_action_ctor_maker_good() -> None:
    Action(get_test_instrument(), OrderSide.BID, LiquidityType.MAKER, 15, 15.6)


def test_action_ctor_maker_no_price_failure() -> None:
    with pytest.raises(AssertionError):
        Action(get_test_instrument(), OrderSide.BID, LiquidityType.MAKER, 15, None)
