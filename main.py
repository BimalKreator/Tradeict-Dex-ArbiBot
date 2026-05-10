import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.binance_fetcher import get_active_usdt_futures
from services.token_mapper import map_symbol_to_chains
from services.price_fetcher import fetch_filtered_prices
from services.data_streamer import binance_ws_loop, dexscreener_poll_loop
from services.spread_calculator import calculate_spreads
from database.db_manager import init_db, get_mapped_addresses
from database.redis_manager import get_filters, set_filters

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.top_symbols = []


class FilterBody(BaseModel):
    min_liquidity: float
    min_volume: float


@app.on_event("startup")
async def startup_event():
    init_db()
    symbols = get_active_usdt_futures()
    top_50 = symbols[:50]
    app.state.top_symbols = top_50
    for symbol in top_50:
        base_symbol = symbol.replace("USDT", "")
        if not get_mapped_addresses(base_symbol):
            map_symbol_to_chains(base_symbol)
    asyncio.create_task(binance_ws_loop())
    asyncio.create_task(dexscreener_poll_loop(top_50))


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
    return calculate_spreads(app.state.top_symbols)


@app.get("/get-active-tokens")
def get_active_tokens():
    return {"active_tokens": app.state.top_symbols}


@app.get("/get-filters")
def api_get_filters():
    return get_filters()


@app.post("/update-filters")
def api_update_filters(body: FilterBody):
    set_filters(body.min_liquidity, body.min_volume)
    return {"status": "ok"}

