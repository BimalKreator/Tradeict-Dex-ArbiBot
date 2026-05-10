from database.redis_manager import get_all_prices


def calculate_spreads(symbols):
    results = []
    for symbol in symbols:
        prices = get_all_prices(symbol)
        binance_price = prices.pop("binance_futures", None)
        if len(prices) < 2:
            continue

        highest_dex = max(prices, key=lambda k: prices[k])
        lowest_dex = min(prices, key=lambda k: prices[k])
        highest_price = prices[highest_dex]
        lowest_price = prices[lowest_dex]
        spread_percentage = ((highest_price - lowest_price) / lowest_price) * 100

        results.append(
            {
                "symbol": symbol,
                "binance_price": binance_price,
                "highest_dex": highest_dex,
                "highest_price": highest_price,
                "lowest_dex": lowest_dex,
                "lowest_price": lowest_price,
                "spread_percentage": spread_percentage,
            }
        )

    return results
