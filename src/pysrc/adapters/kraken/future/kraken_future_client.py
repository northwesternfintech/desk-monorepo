from pysrc.adapters.kraken.future.containers import TradeHistory, TradeHistoryType, TakerSide, Orderbook, OrderbookEntry
import requests
from pysrc.util.types import OrderSide

FUTURES_API_LIVE_BASE_URL = "https://futures.kraken.com/derivatives/api/v3/"
FUTURES_API_TESTNET_BASE_URL = "https://demo-futures.kraken.com/derivatives/api/v3/"

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

    def get_history(self, symbol: str, lastTime: int = 0) -> list[TradeHistory]:
        url = f'{self.base_url}history'
        params = f'symbol={symbol}'
        if lastTime > 0:
            params += f"&lastTime={lastTime}"

        response = requests.get(f'{url}?{params}').json()

        return list(map(
            lambda x: self._serialize_history(symbol, x),
            response["history"]
        ))

    def get_orderbook(self, symbol: str) -> Orderbook:
        url = f'{self.base_url}orderbook'
        params = f'symbol={symbol}'

        response = requests.get(f'{url}?{params}').json()

        asks = list(map(lambda x: self._serialize_order_from_orderbook(True, x), response["orderBook"]["asks"]))
        bids = list(map(lambda x: self._serialize_order_from_orderbook(False, x), response["orderBook"]["bids"]))

        return Orderbook(symbol, asks, bids)

    # def get_open_positions(self) -> list[OpenPosition]:
    #     pass

    # def get_open_orders(self) -> list[Order]:
    #     pass
    
    # def get_order_statuses(self, order_ids: list[str]) -> list[Order]:
    #     pass

    # def send_order(self, order_request: OrderRequest) -> OrderStatus:
    #     pass

    # def batch_send_order(self, order_request: OrderRequest) -> dict[str, OrderStatus]:
    #     # returns map of order_id -> status
    #     pass

    # def edit_order(self, order_id: str, new_order_request: OrderRequest) -> None:
    #     pass

    # def batch_edit_order(self, new_order_requests: dict[str, OrderRequest]) -> list[str]:
    #     # returns map of order_id -> status
    #     pass

    # def cancel_order(self, order_id: str, process_before: str) -> OrderStatus:
    #     pass

    # def batch_cancel_order(self, order_ids: list[str]) -> dict[str, OrderStatus]:
    #     # returns map of order_id -> status
    #     pass

    # def cancel_all_orders(self, symbol: str) -> list[str]:
    #     # returns list of cancelled order ids
    #     pass

    # Helpers

    def _string_to_history_type(self, history_type: str) -> TradeHistoryType:
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
                return TradeHistoryType.BLOCK
            case _:
                return TradeHistoryType.FILL

    def _string_to_taker_side(self, side: str) -> TakerSide:
        match side:
            case "buy":
                return TakerSide.BUY
            case "sell":
                return TakerSide.SELL
            case _:
                return TakerSide.BUY

    def _serialize_history(self, symbol: str, hist: dict) -> TradeHistory:
        return TradeHistory(
            symbol,
            hist.get("price", 0),
            self._string_to_taker_side(hist.get("side", "")),
            hist.get("side"),
            hist.get("time", ""),
            hist.get("trade_id", 0),
            self._string_to_history_type(hist.get("type", "")),
            hist.get("uid"),
            hist.get("instrument_identification_type"),
            hist.get("isin"),
            hist.get("execution_venue"),
            hist.get("price_notation"),
            hist.get("price_currency"),
            hist.get("notional_amount"),
            hist.get("notional_currency"),
            hist.get("publication_time"),
            hist.get("publication_venue"),
            hist.get("transaction_identification_code"),
            hist.get("to_be_cleared")
        )

    def _serialize_order_from_orderbook(self, isAsk: bool, x: list[float]) -> OrderbookEntry:
        if isAsk:
            return OrderbookEntry(OrderSide.ASK, x[1], x[0])
        else:
            return OrderbookEntry(OrderSide.BID, x[1], x[0])