from database.redis_manager import get_all_prices


def calculate_spreads(symbols):
    results = []
    for symbol in symbols:
        prices = get_all_prices(symbol)
        binance_price = prices.pop("binance_futures", None)
        valid_prices = {}
        for dex, price in prices.items():
            try:
                p = float(price)
                if p > 0.00000001:
                    valid_prices[dex] = p
            except (ValueError, TypeError):
                continue
        if len(valid_prices) < 2:
            continue

        highest_dex = max(valid_prices, key=valid_prices.get)
        lowest_dex = min(valid_prices, key=valid_prices.get)
        highest_price = valid_prices[highest_dex]
        lowest_price = valid_prices[lowest_dex]
        spread_percentage = ((highest_price - lowest_price) / lowest_price) * 100

        binance_fee = 0.10
        highest_dex_fee = 0.30
        lowest_dex_fee = 0.30
        total_fee = binance_fee + highest_dex_fee + lowest_dex_fee
        net_spread = spread_percentage - total_fee

        results.append(
            {
                "symbol": symbol,
                "binance_price": binance_price,
                "highest_dex": highest_dex,
                "highest_price": highest_price,
                "lowest_dex": lowest_dex,
                "lowest_price": lowest_price,
                "spread_percentage": spread_percentage,
                "binance_fee": binance_fee,
                "highest_dex_fee": highest_dex_fee,
                "lowest_dex_fee": lowest_dex_fee,
                "total_fee": total_fee,
                "net_spread": net_spread,
            }
        )

    return results
