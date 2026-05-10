import os

import redis

REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("REDIS_URL is not set.")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def set_price(symbol: str, exchange: str, price) -> None:
    key = f"price:{symbol}:{exchange}"
    redis_client.set(key, str(price))


def get_price(symbol: str, exchange: str):
    key = f"price:{symbol}:{exchange}"
    return redis_client.get(key)


def get_all_prices(symbol):
    pattern = f"price:{symbol}:*"
    keys = redis_client.keys(pattern)
    result = {}
    for key in keys:
        parts = key.split(":", 2)
        if len(parts) < 3:
            continue
        exchange_name = parts[2]
        raw = redis_client.get(key)
        if raw is None:
            continue
        result[exchange_name] = float(raw)
    return result
