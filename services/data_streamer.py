import asyncio

import requests

from database.redis_manager import set_price
from services.price_fetcher import fetch_filtered_prices


async def binance_poll_loop():
    while True:
        try:
            response = await asyncio.to_thread(
                requests.get,
                "https://fapi.binance.com/fapi/v1/ticker/price",
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    for item in data:
                        set_price(
                            item["symbol"],
                            "binance_futures",
                            item["price"],
                        )
                print("Binance REST Update: Fetched all prices")
            else:
                print(f"Binance REST Error: HTTP {response.status_code}")
        except Exception as e:
            print(f"Binance REST Error: {e}")
        await asyncio.sleep(2)


async def dexscreener_poll_loop(symbols):
    while True:
        for symbol in symbols:
            try:
                base_symbol = symbol.replace("USDT", "")
                prices = await asyncio.to_thread(
                    fetch_filtered_prices, base_symbol
                )
                print(
                    f"DexScreener Update: {base_symbol} -> saved {len(prices)} pair prices"
                )
                if not prices:
                    continue
                for pair in prices:
                    chain_id = pair.get("chainId")
                    dex_id = pair.get("dexId")
                    price_usd = pair.get("priceUsd")
                    if chain_id is None or dex_id is None or price_usd is None:
                        continue
                    set_price(symbol, f"{chain_id}_{dex_id}", price_usd)
            except Exception as e:
                print(f"DexScreener Error for {symbol}: {e}")
        await asyncio.sleep(5)
