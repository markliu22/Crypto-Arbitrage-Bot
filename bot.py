import ccxt
import asyncio

# Initialize exchanges with ccxt
exchanges = {
    'bitstamp': ccxt.bitstamp(),
    'coinbasepro': ccxt.coinbasepro(),  # Note: Coinbase Pro is used instead of Coinbase as it's what ccxt interfaces with
    'kraken': ccxt.kraken(),
}

# Define trading fees for each exchange (assumed values, please verify with the actual exchange)
exchanges_fees = {
    'bitstamp': {'trading_fee': 0.25, 'withdrawal_fee': 5.00},
    'coinbasepro': {'trading_fee': 0.50, 'withdrawal_fee': 2.50},
    'kraken': {'trading_fee': 0.26, 'withdrawal_fee': 0.00},
}

async def fetch_prices():
    prices = {}
    for exchange_id in exchanges:
        exchange = exchanges[exchange_id]
        try:
            # Fetch the ticker for BTC/USD
            ticker = exchange.fetch_ticker('BTC/USD')
            last_price = ticker['last']
            prices[exchange_id] = {'rate': last_price, **exchanges_fees[exchange_id]}
        except Exception as e:
            print(f"Failed to fetch data for {exchange_id}: {e}")
    return prices

def find_arbitrage_opportunities(prices):
    best_buy = {'exchange': None, 'effective_rate': float('inf')}
    best_sell = {'exchange': None, 'effective_rate': 0}

    for exchange, info in prices.items():
        effective_buy_rate = info['rate'] * (1 + info['trading_fee'] / 100)
        effective_sell_rate = info['rate'] * (1 - info['trading_fee'] / 100) - info['withdrawal_fee']

        if effective_buy_rate < best_buy['effective_rate']:
            best_buy = {'exchange': exchange, 'effective_rate': effective_buy_rate}
        if effective_sell_rate > best_sell['effective_rate']:
            best_sell = {'exchange': exchange, 'effective_rate': effective_sell_rate}

    potential_profit = best_sell['effective_rate'] - best_buy['effective_rate']

    if potential_profit > 0:
        print(f"Arbitrage Opportunity: Buy on {best_buy['exchange']} at ${best_buy['effective_rate']} and sell on {best_sell['exchange']} at ${best_sell['effective_rate']}. Potential profit: ${potential_profit} per BTC")
    else:
        print("No arbitrage opportunities found.")

async def main():
    prices = await fetch_prices()
    find_arbitrage_opportunities(prices)

# Run the async main function
asyncio.run(main())
