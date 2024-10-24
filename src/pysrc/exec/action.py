from pysrc.util.types import OrderSide, LiquidityType
from pysrc.util.instrument import Instrument

from typing import Optional


class Action:
    def __init__(
        self,
        instrument: Instrument,
        side: OrderSide,
        liquidity_type: LiquidityType,
        quantity: float,
        price: Optional[float],
    ):
        self.instrument = instrument
        self.side = side
        self.liquidity_type = liquidity_type
        self.quantity = quantity
        self.price: Optional[float] = price
        if self.liquidity_type == LiquidityType.MAKER:
            assert self.price is not None
