from pysrc.util.types import Asset

_kraken_to_asset = {
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
}
_asset_to_kraken = {
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
}


def kraken_to_asset(kraken_name: str) -> Asset:
    return _kraken_to_asset[kraken_name]


def asset_to_kraken(asset: Asset) -> str:
    return _asset_to_kraken[asset]
