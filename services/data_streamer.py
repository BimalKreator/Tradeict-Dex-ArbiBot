import asyncio
import json

import websockets

from database.redis_manager import set_price
from services.price_fetcher import fetch_filtered_prices

_BINANCE_FUTURES_MINI_TICKER_WS = "wss://fstream.binance.com/ws/!miniTicker@arr"


async def binance_ws_loop():
    while True:
        try:
            async with websockets.connect(_BINANCE_FUTURES_MINI_TICKER_WS) as ws:
                print("Binance WS Connected!")
                async for raw in ws:
                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(data, list):
                        continue
                    for item in data:
                        symbol = item.get("s")
                        price = item.get("c")
                        if symbol is None or price is None:
                            continue
                        set_price(symbol, "binance_futures", price)
                        if symbol in ["SOLUSDT", "ETHUSDT"]:
                            print(f"Binance Update: {symbol} -> {price}")
        except Exception as e:
            print(f"Binance WS Error: {e}")
            await asyncio.sleep(5)


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
