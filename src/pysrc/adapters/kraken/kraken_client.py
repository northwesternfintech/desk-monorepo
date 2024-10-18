import requests
from pysrc.adapters.kraken.containers import SystemStatus, AssetInfo, AssetPair, AssetPairInfo, OHLCData, AssetStatus, OHLCTick
from typing import Optional, Dict
from pysrc.util.types import Asset, Market, OrderSide
from pysrc.adapters.messages import TradeMessage, SnapshotMessage, SpreadMessage
from enum import Enum
from typing import Type, TypeVar

class KrakenClient:
    def __init__(self, base_url: str = "https://api.kraken.com/0/public/", currency: str = "USDT"):
        self._base_url = base_url
        self._currency = currency
        self._kraken_to_asset = {"XXBTZUSD" : "BTC"} # UNFINISHED
        self._asset_to_kraken = {"BTC" : "XXBTZUSD"}
    
    def _get(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> dict:
        """Helper method to send GET requests and handle HTTP errors."""
        url = f"{self._base_url}{endpoint}"
        
        try:
            response = requests.get(url, params=params)  
            response.raise_for_status()  
            res = response.json() 

            if res['error']:
                raise ValueError(f"API Error: {response['error']}")

            return res 

        except requests.exceptions.RequestException as e:
            return {'error': [str(e)], 'result': {}}
    
    def get_system_status(self) -> SystemStatus:
        response = self._get('SystemStatus')
        return SystemStatus[response['result']['status'].upper()]

    
    def get_asset_info(self, asset: Asset, aclass: str = "currency") -> AssetInfo:
        params = {
        'asset': asset.name,  
        'aclass': aclass 
        }

        response = self._get("Assets", params)
        asset_data = response['result'][asset.name]  
        return AssetInfo(
            asset=asset,
            asset_name=asset_data['altname'],
            altname=asset_data['altname'],
            decimals=asset_data['decimals'],
            collateral_value=asset_data.get('collateral_value'),  
            status = AssetStatus[asset_data['status'].replace(' ', '_').upper()]
        )
    
    def get_tradeable_asset_pairs(self, pairs: list[AssetPair], info: str = "info") -> Dict[str, AssetPairInfo]:
        assert info in ["info", "leverage", "fees", "margin"]
        pair_param = ",".join([f"{pair.asset1.name}/{pair.asset2.name}" for pair in pairs])

        params = {
        'pair': pair_param,
        'info': info,
        }
        response = self._get('AssetPairs', params=params)

        asset_pairs = {}
        for pair_name, pair_data in response['result'].items():
            asset_pairs[pair_name] = AssetPairInfo(
                altname=pair_data['altname'],
                wsname=pair_data.get('wsname'),  
                aclass_base=pair_data['aclass_base'],
                base=pair_data['base'],
                aclass_quote=pair_data['aclass_quote'],
                quote=pair_data['quote']
            )
        return asset_pairs

    def get_ohlc_data(self, asset: Asset, interval: int = 1, since: Optional[int] = None) -> OHLCData:
        assert interval in [1, 5, 15, 30, 60, 240, 1440, 10080, 21600]

        pair_param = f"{asset.name}USD"
        
        params = {
            'pair': pair_param,
            'interval': interval
        }

        if since:
            params['since'] = since

        response = self._get('OHLC', params=params)

        last_timestamp = response['result'].get('last', None)

        pair_name = list(response['result'].keys())[0]
        tick_data = response['result'][self._asset_to_kraken[asset.name]]

        ohlc_ticks = [
            OHLCTick(
                time=tick[0],
                open=tick[1],
                high=tick[2],
                low=tick[3],
                close=tick[4],
                vwap=tick[5],
                volume=tick[6],
                count=tick[7]
            ) for tick in tick_data
        ]

        return OHLCData(
            asset=Asset[self._kraken_to_asset[pair_name]],
            ticks=ohlc_ticks,
            last=last_timestamp
        )
    def get_order_book(self, asset: Asset, count: int = 100) -> SnapshotMessage:
        assert 1 <= count <= 500

        pair_param = f"{asset.name}USD"

        params = {
            'pair': pair_param,
            'count': count
        }

        response = self._get('Depth', params=params)
        #print(response)
        order_book_data = response['result'][self._asset_to_kraken[asset.name]]

        bids = [(price, volume) for price, volume, _ in order_book_data['bids']]
        asks = [(price, volume) for price, volume, _ in order_book_data['asks']]
        timestamp = int(order_book_data['bids'][0][2])
        feedcode = pair_param

        return SnapshotMessage(
            time=timestamp,
            feedcode=feedcode,
            bids=bids,
            asks=asks,
            market=Market.KRAKEN_SPOT
        )

    def get_recent_trades(self, asset: Asset, since: int = None, count: int = 1000) -> list[TradeMessage]:
        assert 1 <= count <= 1000

        pair_param = f"{asset.name}USD"

        params = {
            'pair': pair_param,
            'count': count
        }

        if since:
            params['since'] = str(since)

        response = self._get('Trades', params=params)

        trade_data = response['result'][self._asset_to_kraken[asset.name]]
        trades = []

        for trade in trade_data:
            price = float(trade[0])
            quantity = float(trade[1])
            timestamp = int(trade[2])
            side = OrderSide.BID if trade[3] == 'b' else OrderSide.ASK

            trades.append(TradeMessage(
                time=timestamp,
                feedcode=pair_param,
                n_trades=1,  
                price=price,
                quantity=quantity,
                side=side,
                market=Market.KRAKEN_SPOT
            ))

        return trades

    def get_recent_spreads(self, asset: Asset, since: int = None) -> list[SpreadMessage]:
        pair_param = f"{asset.name}USD"

        params = {
            'pair': pair_param
        }

        if since:
            params['since'] = str(since)

        response = self._get('Spread', params=params)

        spread_data = response['result'][self._asset_to_kraken[asset.name]]
        spreads = []

        for spread in spread_data:
            timestamp = int(spread[0])
            bid = float(spread[1])
            ask = float(spread[2])

            spreads.append(SpreadMessage(
                time=timestamp,
                feedcode=pair_param,
                bid=bid,
                ask=ask
            ))

        return spreads
