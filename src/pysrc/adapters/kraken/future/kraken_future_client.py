from pysrc.adapters.kraken.future.containers import OpenPosition, Order, OrderRequest, OrderStatus


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

    def public_get_history(self, symbol: str, lastTime: int) -> list(TradeMessage):
        pass

    def public_get_orderbook(self, symbol: str) -> Orderbook:
        pass

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