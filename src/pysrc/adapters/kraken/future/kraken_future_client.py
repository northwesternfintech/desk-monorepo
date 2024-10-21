from pysrc.adapters.kraken.future.containers import OpenPosition, Order, OrderRequest, OrderStatus, TradeHistory, TradeHistoryType, TakerSide
from typing import Optional
import requests

FUTURES_API_LIVE_BASE_URL = "https://futures.kraken.com/derivatives/api/v3/"
FUTURES_API_TESTNET_BASE_URL = "https://demo-futures.kraken.com/derivatives/api/v3/"

from pysrc.adapters.messages import TradeMessage

class KrakenFutureClient:
    def __init__(
            self,
            api_key: str,
            authent: str,
            use_live_api: bool = True,
            ):
        self.base_url: str = (
            FUTURES_API_LIVE_BASE_URL if use_live_api else FUTURES_API_TESTNET_BASE_URL
        )

    def get_history(self, symbol: str, lastTime: Optional[int]) -> list[TradeMessage]:
        url = f'{self.base_url}/history'
        params = f'symbol={symbol}'
        if lastTime is not None:
            params += f"lastTime={lastTime}"

        response = requests.get(f'{url}?{params}').json()

        return map(
            lambda x: _serialize_history(symbol, x)
            response["history"]
        )

    def get_orderbook(self, symbol: str) -> Orderbook:
        url = f'{self.base_url}/orderbook'
        params = f'symbol={symbol}'

        response = request.get(f'{url}?{params}').json()

        asks = map(lambda x: _serialize_order_from_orderbook(symbol, True, x), response["orderBook"]["asks"])
        bids = map(lambda x: _serialize_order_from_orderbook(symbol, False, x), response["orderBook"]["bids"])

        return Orderbook(symbol, asks, bids)

    def get_open_positions(self) -> list[OpenPosition]:
        pass

    def get_open_orders(self) -> list[Order]:
        pass
    
    def get_order_statuses(self, order_ids: list[str]) -> list[Order]:
        pass

    def send_order(self, order_request: OrderRequest) -> OrderStatus:
        pass

    def batch_send_order(self, order_request: OrderRequest) -> dict[str, OrderStatus]:
        # returns map of order_id -> status
        pass

    def edit_order(self, order_id: str, new_order_request: OrderRequest) -> None:
        pass

    def batch_edit_order(self, new_order_requests: dict[str, OrderRequest]) -> list[str]:
        # returns map of order_id -> status
        pass

    def cancel_order(self, order_id: str, process_before: str) -> OrderStatus:
        pass

    def batch_cancel_order(self, order_ids: list[str]) -> dict[str, OrderStatus]:
        # returns map of order_id -> status
        pass

    def cancel_all_orders(self, symbol: str) -> list[str]:
        # returns list of cancelled order ids
        pass

    # Helpers

    def _string_to_history_type(history_type: str):
        match history_type:
            case "fill":
                return TradeHistoryType.FILL
            case "liquidation":
                return TradeHistoryType.LIQUIDATION
            case "assignment":
                return TradeHistoryType.ASSIGNMENT
            case "termination":
                return TradeHistoryType.TERMINATION
            case "block":
                return TradeHistory.BLOCK
    
    def _string_to_taker_side(side: str):
        match side:
            case "buy":
                return TakerSide.BUY
            case "sell":
                return TakerSide.SELL

    def _serialize_history(symbol, hist):
        history_type = 0
        
        return TradeHistory(
            hist["price"],
            _string_to_taker_side(hist["side"]),
            hist["size"],
            hist["time"],
            hist["trade_id"],
            _string_to_history_type(hist["type"]),
            hist["uid"],
            hist["instrument_identification_type"],
            hist["isin"],
            hist["execution_venue"],
            hist["price_notation"],
            hist["price_currency"],
            hist["notional_amount"],
            hist["notional_currency"],
            hist["publication_time"],
            hist["publication_venue"],
            hist["transaction_identification_code"],
            hist["to_be_cleared"]
        )
    
    def _serialize_order_from_orderbook(symbol: str, isAsk: bool, x: list(float)):
        if isAsk:
            return Order(OrderType.LMT, symbol, OrderSide.ASK, x[1], x[0])
        else:
            return Order(OrderType.LMT, symbol, OrderSide.BID, x[1], x[0])