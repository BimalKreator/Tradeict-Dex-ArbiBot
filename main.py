import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.binance_fetcher import get_active_usdt_futures
from services.token_mapper import map_symbol_to_chains
from services.price_fetcher import fetch_filtered_prices
from services.data_streamer import binance_ws_loop, dexscreener_poll_loop
from services.spread_calculator import calculate_spreads
from database.db_manager import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

test_symbols = ["SOLUSDT", "ETHUSDT", "BTCUSDT"]


@app.on_event("startup")
async def startup_event():
    init_db()
    asyncio.create_task(binance_ws_loop())
    asyncio.create_task(dexscreener_poll_loop(test_symbols))

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Tradeict Arbitrage Bot is running"}

@app.get("/symbols")
def get_symbols():
    return get_active_usdt_futures()


@app.get("/map/{symbol}")
def map_symbol(symbol: str):
    return map_symbol_to_chains(symbol)


@app.get("/prices/{symbol}")
def prices(symbol: str):
    return fetch_filtered_prices(symbol)


@app.get("/get-arbitrage-data")
def get_arbitrage_data():
    return calculate_spreads(test_symbols)


@app.get("/get-active-tokens")
def get_active_tokens():
    return {"active_tokens": test_symbols}