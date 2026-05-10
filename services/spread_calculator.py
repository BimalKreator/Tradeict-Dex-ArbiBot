from database.redis_manager import get_all_prices


def calculate_spreads(symbols):
    results = []
    for symbol in symbols:
        prices = get_all_prices(symbol)
        binance_price = prices.pop("binance_futures", None)
        valid_prices = {
            dex: float(price)
            for dex, price in prices.items()
            if price is not None and float(price) > 0
        }
        if len(valid_prices) < 2:
            continue

        highest_dex = max(valid_prices, key=valid_prices.get)
        lowest_dex = min(valid_prices, key=valid_prices.get)
        highest_price = valid_prices[highest_dex]
        lowest_price = valid_prices[lowest_dex]
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
