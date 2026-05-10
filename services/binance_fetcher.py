import requests


def get_active_usdt_futures() -> list[str]:
    response = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo", timeout=10)
    response.raise_for_status()
    symbols = response.json().get("symbols", [])

    return [
        symbol["symbol"]
        for symbol in symbols
        if symbol.get("quoteAsset") == "USDT"
        and symbol.get("status") == "TRADING"
        and symbol.get("contractType") == "PERPETUAL"
    ]