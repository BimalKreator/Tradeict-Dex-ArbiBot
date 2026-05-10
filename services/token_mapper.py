import requests

from database.db_manager import save_token_mapping

_ALLOWED_CHAINS = frozenset({"arbitrum", "base", "polygon", "bsc"})
_MIN_LIQUIDITY_USD = 50000


def map_symbol_to_chains(symbol):
    url = f"https://api.dexscreener.com/latest/dex/search?q={symbol}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    pairs = data.get("pairs") or []

    target = symbol.upper()
    mapped = []

    for pair in pairs:
        chain_id = pair.get("chainId")
        if chain_id not in _ALLOWED_CHAINS:
            continue

        base_token = pair.get("baseToken") or {}
        base_symbol = base_token.get("symbol")
        if not base_symbol or base_symbol.upper() != target:
            continue

        liquidity = pair.get("liquidity") or {}
        usd = liquidity.get("usd")
        if usd is None or float(usd) <= _MIN_LIQUIDITY_USD:
            continue

        address = base_token.get("address")
        if not address:
            continue

        save_token_mapping(symbol, chain_id, address, usd)
        mapped.append(pair)

    return mapped
