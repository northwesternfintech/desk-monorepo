from typing import Optional
from pysrc.util.types import Asset, Market

_kraken_to_asset = {
    Market.KRAKEN_SPOT: {
        "XXBTZUSD": Asset.BTC,
        "XETHZUSD": Asset.ETH,
        "XWIFZUSD": Asset.WIF,
        "XXRPZUSD": Asset.XRP,
        "XSOLZUSD": Asset.SOL,
        "XDOGEZUSD": Asset.DOGE,
        "XTRXZUSD": Asset.TRX,
        "XADAZUSD": Asset.ADA,
        "XAVAXZUSD": Asset.AVAX,
        "XSHIBZUSD": Asset.SHIB,
        "XDOTZUSD": Asset.DOT,
    },
    Market.KRAKEN_USD_FUTURE: {
        "PF_XBTUSD": Asset.BTC,
        "PF_ETHUSD": Asset.ETH,
        "PF_WIFUSD": Asset.WIF,
        "PF_XRPUSD": Asset.XRP,
        "PF_SOLUSD": Asset.SOL,
        "PF_DOGEUSD": Asset.DOGE,
        "PF_TRXUSD": Asset.TRX,
        "PF_ADAUSD": Asset.ADA,
        "PF_AVAXUSD": Asset.AVAX,
        "PF_SHIBUSD": Asset.SHIB,
        "PF_DOTUSD": Asset.DOT,
    }
}
_asset_to_kraken = {
    Market.KRAKEN_SPOT: {
        Asset.BTC: "XXBTZUSD",
        Asset.ETH: "XETHZUSD",
        Asset.WIF: "XWIFZUSD",
        Asset.XRP: "XXRPZUSD",
        Asset.SOL: "XSOLZUSD",
        Asset.DOGE: "XDOGEZUSD",
        Asset.TRX: "XTRXZUSD",
        Asset.ADA: "XADAZUSD",
        Asset.AVAX: "XAVAXZUSD",
        Asset.SHIB: "XSHIBZUSD",
        Asset.DOT: "XDOTZUSD",
    },
    Market.KRAKEN_USD_FUTURE: {
        Asset.BTC: "PF_XBTUSD",
        Asset.ETH: "PF_ETHUSD",
        Asset.WIF: "PF_WIFUSD",
        Asset.XRP: "PF_XRPUSD",
        Asset.SOL: "PF_SOLUSD",
        Asset.DOGE: "PF_DOGEUSD",
        Asset.TRX: "PF_TRXUSD",
        Asset.ADA: "PF_ADAUSD",
        Asset.AVAX: "PF_AVAXUSD",
        Asset.SHIB: "PF_SHIBUSD",
        Asset.DOT: "PF_DOTUSD",
    }
}


def kraken_to_market(kraken_name: str) -> Market:
    if kraken_name in _kraken_to_asset[Market.KRAKEN_SPOT]:
        return Market.KRAKEN_SPOT
    elif kraken_name in _kraken_to_asset[Market.KRAKEN_USD_FUTURE]:
        return Market.KRAKEN_USD_FUTURE
    
    raise ValueError("Invalid kraken asset label — cannot find market")


def kraken_to_asset(kraken_name: str) -> Asset:
    market = kraken_to_market(kraken_name)

    if kraken_name not in _kraken_to_asset[market]:
        raise ValueError("Invalid kraken asset label — cannot convert to asset enum")
    return _kraken_to_asset[market][kraken_name]


def asset_to_kraken(asset: Asset, market: Market) -> str:
    return _asset_to_kraken[market][asset]
