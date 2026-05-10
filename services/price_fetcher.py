import requests

from database.db_manager import get_mapped_addresses

_MAX_ADDRESSES_PER_REQUEST = 30
_MIN_LIQUIDITY_USD = 50000
_MIN_VOLUME_H24 = 10000


def fetch_filtered_prices(symbol):
    addresses = get_mapped_addresses(symbol)
    if not addresses:
        return []

    batch = addresses[:_MAX_ADDRESSES_PER_REQUEST]
    joined = ",".join(batch)
    url = f"https://api.dexscreener.com/latest/dex/tokens/{joined}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    pairs = data.get("pairs") or []

    filtered = []
    for pair in pairs:
        liquidity = pair.get("liquidity") or {}
        volume = pair.get("volume") or {}
        liq_usd = liquidity.get("usd")
        vol_h24 = volume.get("h24")
        if liq_usd is None or vol_h24 is None:
            continue
        if float(liq_usd) <= _MIN_LIQUIDITY_USD or float(vol_h24) <= _MIN_VOLUME_H24:
            continue

        filtered.append(
            {
                "dexId": pair.get("dexId"),
                "chainId": pair.get("chainId"),
                "priceUsd": pair.get("priceUsd"),
                "liquidity": liquidity,
                "volume": volume,
            }
        )

    return filtered
