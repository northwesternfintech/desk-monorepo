from pysrc.adapters.kraken.future.containers import OpenPosition, Order, OrderRequest, OrderStatus
import requests

from pysrc.adapters.kraken.future.utils import str_to_position_side

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

        self._private_session = requests.Session()
        self._private_session.headers.update({"APIKey": api_key, "Authent": api_key})

    def _make_private_request(self, api_route: str) -> dict:
        url = self.base_url + api_route

        res = self._private_session.get(url).json()
        if res["result"] == "error":
            raise ValueError(f"Route {api_route} failed with error {res["errors"]}")
        
        return res

    def get_open_positions(self) -> list[OpenPosition]:
        route = "openpositions"
        res = self._make_private_request(route)
        
        open_positions_json = res["openPositions"]
        open_positions = []
        for position_json in open_positions_json:
            position_side = str_to_position_side(position_json["side"])
            symbol = position_json["symbol"]
            price = position_json["price"]
            fill_time = position_json["fillTime"]
            size = position_json["size"]

            position = OpenPosition(
                position_side,
                symbol,
                price,
                fill_time,
                size
            )

            open_positions.append(position)

        return open_positions


    def get_open_orders(self) -> list[Order]:
        route = "openorders"
        res = self._make_private_request(route)

        open_orders_json = res["openOrders"]
        open_orders = []
        for order_json in open_orders_json:
            order_id = order_json["order_id"]
            symbol = order_json["symbol"]
            order_type = str_to_order_type(order_json["orderType"])
            limit_price = order_json["limitPrice"]
            unfilled_size = order_json["unfilledSize"]
            staus = str_to_order_status(order_json["status"])
            filled_size = order_json["filledSize"]
            reduce_only = order_json["reduceOnly"]
            lastUpdateTime = order_json["lastUpdateTime"]

    
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