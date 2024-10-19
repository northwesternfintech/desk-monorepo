

class TradeHistory:
    def __init__(
        self,
        price: float,
        side: Optional[OrderSide],
        size: float,
        time: str,
        trade_id: int,
        type: HistoryType,
        uid: str,
        instrument_identification_type: str,
        isin: str,
        price_notation: str,
        price_currency: str,
        notional_amount: float,
        notional_currency: str,
        publication_time: str,
        publication_venue: str,
        transaction_identification_code: str,
        to_be_cleared: bool
    )