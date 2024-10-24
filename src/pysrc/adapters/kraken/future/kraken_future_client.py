import base64
import hashlib
import hmac
import json
import time
import urllib
from typing import Optional

import requests

from pysrc.adapters.kraken.future.containers import (OpenPosition, Order,
                                                     OrderRequest, OrderStatus,
                                                     TradeHistory, TradeHistoryType,
                                                     TakerSide)
from pysrc.adapters.kraken.future.utils import (order_side_to_str,
                                                order_status_to_str,
                                                order_type_to_str,
                                                price_unit_to_str,
                                                str_to_order_side,
                                                str_to_order_status,
                                                str_to_order_type,
                                                str_to_position_side,
                                                str_to_trigger_signal,
                                                trigger_signal_to_str,
                                                url_encode_dict,
                                                serialize_history)

from pysrc.adapters.messages import SnapshotMessage
from pysrc.util.types import Market

FUTURES_API_LIVE_BASE_URL = "https://futures.kraken.com/derivatives"
FUTURES_API_TESTNET_BASE_URL = "https://demo-futures.kraken.com/derivatives"


class KrakenFutureClient:
    def __init__(
            self,
            public_key: str,
            private_key: str,
            use_live_api: bool = True,
            ):
        self._base_url: str = (
            FUTURES_API_LIVE_BASE_URL if use_live_api else FUTURES_API_TESTNET_BASE_URL
        )
        self._public_key = public_key
        self._private_key = private_key

        self._private_session = requests.Session()
        self._public_session = requests.Session()

    def _calculate_authent(self, encoded_data: str, api_route: str) -> str:
        msg = encoded_data + api_route
        msg = hashlib.sha256(msg.encode('utf-8')).digest()
        decoded_key = base64.b64decode(self._private_key)

        authent = hmac.new(decoded_key, msg, hashlib.sha512)
        return base64.b64encode(authent.digest()).decode()

    def _make_private_request(self, request_type: str, api_route: str, params: dict[str] = {}, data: dict[str] = {}) -> dict:
        url = self._base_url + api_route

        encoded_data = url_encode_dict(data)
        headers = {"APIKey": self._public_key, "Authent": self._calculate_authent(encoded_data, api_route)}

        req_func = None
        match request_type:
            case "POST":
                req_func = self._private_session.post
            case "GET":
                req_func = self._private_session.get
            case _:
                raise ValueError(f"Unknown request type '{request_type}'")
        
        res = req_func(url, headers=headers, params=params, data=encoded_data).json()
        print(res)
        if res["result"] == "error":
            err = None
            if "errors" in res:
                err = res["errors"]
            elif "error" in res:
                err = res["error"]
            else:
                err = "Unknown error"

            raise ValueError(f"Route {api_route} failed with error '{err}'")
        
        return res

    def _make_public_request(self, request_type: str, api_route: str, params: dict[str] = {}) -> dict:
        url = self._base_url + api_route

        res = None
        match request_type:
            case "POST":
                res = self._public_session.post(url, params=params).json()
            case "GET":
                res = self._public_session.get(url, params=params).json()
            case _:
                raise ValueError(f"Unknown request type '{request_type}'")
        
        # res = req_func(url, params=params).json()
        # print(res)
        if res["result"] == "error":
            err = None
            if "errors" in res:
                err = res["errors"]
            elif "error" in res:
                err = res["error"]
            else:
                err = "Unknown error"

            raise ValueError(f"Route {api_route} failed with error '{err}'")
        
        return res

    def get_open_positions(self) -> list[OpenPosition]:
        route = "/api/v3/openpositions"
        res = self._make_private_request("GET", route)
        
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

    def get_history(self, symbol: str, lastTime: int = 0) -> list[TradeHistory]:

        params = {
            "symbol": symbol
        }
        if lastTime > 0:
            params["lastTime"] = lastTime

        response = self._make_public_request("GET", "/history", params = params)

        return list(map(
            lambda x: serialize_history(symbol, x),
            response["history"]
        ))

    def get_orderbook(self, symbol: str) -> SnapshotMessage:
        params = {
            "symbol": symbol
        }

        response = self._make_public_request("GET", "/orderbook", params = params)

        time = response["serverTime"]
        asks = response["orderBook"]["asks"]
        bids = response["orderBook"]["bids"]

        return SnapshotMessage(time, symbol, bids, asks, Market.KRAKEN_USD_FUTURE)

    # def get_open_positions(self) -> list[OpenPosition]:
    #     pass

    def get_open_orders(self) -> list[Order]:
        route = "/api/v3/openorders"
        res = self._make_private_request("GET", route)

        open_orders_json = res["openOrders"]
        open_orders = []
        for order_json in open_orders_json:
            order_id = order_json["order_id"]
            symbol = order_json["symbol"]
            side = str_to_order_side(order_json["side"])
            order_type = str_to_order_type(order_json["orderType"])
            limit_price = order_json["limitPrice"] if "limitPrice" in order_json else None
            stop_price = order_json["stopPrice"] if "stopPrice" in order_json else None
            unfilled_size = order_json["unfilledSize"]
            status = str_to_order_status(order_json["status"])
            filled_size = order_json["filledSize"] if "filledSize" in order_json else None
            reduce_only = order_json["reduceOnly"]
            trigger_signal = str_to_trigger_signal(order_json["triggerSignal"]) if "triggerSignal" in order_json else None
            last_update_time = order_json["lastUpdateTime"]

            size = unfilled_size
            if filled_size:
                size += filled_size

            order = Order(
                symbol=symbol,
                side=side,
                size=size,
                order_type=order_type,
                status=status,
                limit_price=limit_price,
                stop_price=stop_price,
                order_id=order_id,
                filled_size=filled_size,
                unfilled_size=unfilled_size,
                reduce_only=reduce_only,
                trigger_signal=trigger_signal,
                last_update_time=last_update_time
            )

            open_orders.append(order)

        return open_orders

    
    def get_order_statuses(self, order_ids: list[str]) -> list[Order]:
        route = "/api/v3/orders/status"
        data = {
            "orderIds": order_ids
        }
        res = self._make_private_request(route, data=data)

        open_orders_json = res["openOrders"]
        open_orders = []
        for order_obj_json in open_orders_json:
            order_json = order_obj_json["order"]
            status = str_to_order_status(order_obj_json["status"])

            order_id = order_json["orderId"]
            symbol = order_json["symbol"]
            side = str_to_order_type(order_json["side"])
            size = order_json["quantity"] if "quantity" in order_json else None
            limit_price = order_json["limitPrice"] if "limitPrice" in order_json else None
            filled_size = order_json["filledSize"] if "filledSize" in order_json else None
            reduce_only = order_json["reduceOnly"]
            last_update_time = order_json["lastUpdateTime"]

            order = Order(
                symbol=symbol,
                side=side,
                size=size,
                status=status,
                limit_price=limit_price,
                order_id=order_id,
                filled_size=filled_size,
                reduce_only=reduce_only,
                last_update_time=last_update_time
            )

            open_orders.append(order)

        return open_orders
    
    def send_order(self, order_request: OrderRequest) -> OrderStatus:
        route = "/api/v3/sendorder"

        order = order_request.order
        data = {
            "orderType": order_type_to_str(order.order_type),
            "symbol": order.symbol,
            "side": order_side_to_str(order.side),
            "size": order.size,
            "ProcessBefore": order_request.process_before,
            "limitPrice": order.limit_price,
            "stopPrice": order.stop_price,
            "triggerSignal": trigger_signal_to_str(order.trigger_signal) if order.trigger_signal else None,
            "reduceOnly": order.reduce_only,
            "trailingStopMaxDeviation": order_request.trailing_stop_max_deviation,
            "trailingStopDeviationUnit": price_unit_to_str(order_request.trailing_stop_deviation_unit) if order_request.trailing_stop_deviation_unit else None,
            "limitPriceOffsetValue": order_request.limit_price_offset_value,
            "limitPriceOffsetUnit": price_unit_to_str(order_request.limit_price_offset_unit) if order_request.limit_price_offset_unit else None
        }

        res = self._make_private_request("POST", route, data=data)
        send_status = res["sendStatus"]

        order_status = send_status["status"]
        if order_status != order_status_to_str(OrderStatus.PLACED) and order_status != order_status_to_str(OrderStatus.PLACED) and order_status != order_status_to_str(OrderStatus.PARTIALLY_FILLED):
            order.status = OrderStatus.REJECTED
        else:
            order.status = OrderStatus.PLACED

        order.order_id = send_status["order_id"]

        return order

    def batch_send_order(self, order_requests: list[OrderRequest], process_before: Optional[str]) -> dict[str, OrderStatus]:
        route = "/api/v3/batchorder"
        data = {
            "ProcessBefore": process_before
        }
        
        orders_data = []
        for order_request in order_requests:
            order = order_request.order
            order_data = {
                "order": "send",
                "orderType": order_type_to_str(order.order_type),
                "symbol": order.symbol,
                "side": order_side_to_str(order.side),
                "size": order.size,
                "ProcessBefore": order_request.process_before,
                "limitPrice": order.limit_price,
                "stopPrice": order.stop_price,
                "triggerSignal": trigger_signal_to_str(order.trigger_signal),
                "reduceOnly": order.reduce_only,
                "trailingStopMaxDeviation": order_request.trailing_stop_max_deviation,
                "trailingStopDeviationUnit": price_unit_to_str(order_request.trailing_stop_deviation_unit),
            }

            # this gets sent as a json encoded string rather than a URL parameter, so we need to get rid of None key/values
            keys = order_data.keys()
            for param in keys:
                if order_data[param] is None:
                    order_data.pop(param)

            orders_data.append(order_data)

        data["json"] = orders_data

        res = self._make_private_request(route, data=data)
        send_status = res["sendStatus"]

        order.order_id = send_status["order_id"]
        if send_status["status"] != order_status_to_str(OrderStatus.PLACED):
            order.status = OrderStatus.REJECTED
        else:
            order.status = OrderStatus.PLACED

        return order.status

    def edit_order(self, order_id: str, new_order_request: OrderRequest) -> bool:
        route = "/api/v3/editorder"
        params = {
            "ProcessBefore": new_order_request.process_before
        }
        data = {
            "orderId": order_id,
            "size": new_order_request.order.size,
            "limitPrice": new_order_request.order.limit_price,
            "stopPrice": new_order_request.order.stop_price,
            "trailingStopMaxDeviation": new_order_request.trailing_stop_max_deviation,
            "trailingStopDeviationUnit": price_unit_to_str(new_order_request.trailing_stop_deviation_unit),
        }

        keys = data.keys()
        for param in keys:
            if data[param] is None:
                data.pop(param)

        res = self._make_private_request(route, params=params, data=data)
        edit_status = res["editStatus"]

        return edit_status["status"] == order_status_to_str(OrderStatus.EDITED)

    # def batch_edit_order(self, new_order_requests: dict[str, OrderRequest]) -> list[str]:
    #     # returns map of order_id -> status
    #     pass

    def cancel_order(self, order_id: str, process_before: Optional[str] = None) -> OrderStatus:
        route = "/api/v3/cancelorder"
        data = {
            "ProcessBefore": process_before,
            "order_id": order_id
        }

        res = self._make_private_request("POST", route, data=data)
        cancel_status = res["cancelStatus"]

        try:
            status = str_to_order_status(cancel_status["status"])
            return status
        except:
            # only happens if the order can't be found
            return OrderStatus.REJECTED

    # def batch_cancel_order(self, order_ids: list[str]) -> dict[str, OrderStatus]:
    #     # returns map of order_id -> status
    #     pass

    def cancel_all_orders(self, symbol: str) -> list[str]:
        route = "/api/v3/cancelallorders"
        data = {
            "symbol": symbol
        }

        res = self._make_private_request("POST", route, data=data)
        cancel_status = res["cancelStatus"]
        cancelled_orders = cancel_status["cancelledOrders"]

        cancelled_order_ids = []
        for order in cancelled_orders:
            cancelled_order_ids.append(order["order_id"])

        return cancelled_order_ids
    