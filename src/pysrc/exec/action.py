from pysrc.util.types import OrderSide, LiquidityType
from pysrc.util.instrument import Instrument


class Action:

    def __init__(self, instrument: Instrument, side: OrderSide, type: LiquidityType, price: float, quantity: float):
        self.instrument = instrument
        self.side = side
        self.liquidity_type = type
        self.price = price
        self.quantity = quantity
