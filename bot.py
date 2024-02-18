import ccxt
import asyncio

from config import (BITSTAMP_API_KEY, BITSTAMP_SECRET, COINBASEPRO_API_KEY, 
                    COINBASEPRO_SECRET,KRAKEN_API_KEY, KRAKEN_SECRET)

# Initialize exchanges with ccxt
# Initialize exchanges with ccxt and API credentials
exchanges = {
    # 'bitstamp': ccxt.bitstamp({'apiKey': 'YOUR_BITSTAMP_API_KEY', 'secret': 'YOUR_BITSTAMP_SECRET'}),
    'coinbasepro': ccxt.coinbasepro({'apiKey': COINBASEPRO_API_KEY, 'secret': COINBASEPRO_SECRET}),
    'kraken': ccxt.kraken({'apiKey': KRAKEN_API_KEY, 'secret': KRAKEN_SECRET}),
}

# Adjusted for demonstration; ensure these are correct and include other necessary parameters for your accounts.
exchanges_fees = {
    'bitstamp': {'trading_fee': 0.25, 'withdrawal_fee': 5.00},
    'coinbasepro': {'trading_fee': 0.50, 'withdrawal_fee': 2.50},
    'kraken': {'trading_fee': 0.26, 'withdrawal_fee': 0.00},
}

async def fetch_prices():
    prices = {}
    tasks = []  # List to hold our tasks for asynchronous execution

    # Create a coroutine for each exchange to fetch the ticker
    for exchange_id in exchanges:
        exchange = exchanges[exchange_id]
        task = asyncio.create_task(fetch_ticker(exchange, exchange_id))
        tasks.append(task)
    
    # Wait for all tasks(coroutines) to complete
    results = await asyncio.gather(*tasks)

    # Process results
    for result in results:
        exchange_id, ticker = result
        if ticker:  # If ticker fetch was successful
            last_price = ticker['last']
            prices[exchange_id] = {'rate': last_price, **exchanges_fees[exchange_id]}
    
    return prices

# Helper coroutine to fetch ticker for each exchange
async def fetch_ticker(exchange, exchange_id):
    try:
        ticker = await exchange.fetch_ticker('BTC/USD')
        return exchange_id, ticker
    except Exception as e:
        print(f"Failed to fetch data for {exchange_id}: {e}")
        return exchange_id, None
    
# Ensure to properly close the exchange connections
async def close_exchanges():
    await asyncio.gather(*(exchange.close() for exchange in exchanges.values()))

def place_order(exchange_id, side, amount, price):
    exchange = exchanges[exchange_id]
    symbol = 'BTC/USD'  # TODO: double check symbol is correct for exchange
    type = 'market'  # 'limit' rarely every gets filled
    
    try:
        if side == 'buy':
            # TODO: Adjust 'amount' based on your strategy and capital management
            order = exchange.create_limit_buy_order(symbol, amount, price)
        else:
            order = exchange.create_limit_sell_order(symbol, amount, price)
        print(f"Order placed on {exchange_id}: {order}")
    except Exception as e:
        print(f"Failed to place order on {exchange_id}: {e}")

def find_arbitrage_opportunities(prices):
    best_buy = {'exchange': None, 'effective_rate': float('inf'), 'price': None}
    best_sell = {'exchange': None, 'effective_rate': 0, 'price': None}

    for exchange, info in prices.items():
        effective_buy_rate = info['rate'] * (1 + info['trading_fee'] / 100)
        effective_sell_rate = info['rate'] * (1 - info['trading_fee'] / 100) - info['withdrawal_fee']

        if effective_buy_rate < best_buy['effective_rate']:
            best_buy = {'exchange': exchange, 'effective_rate': effective_buy_rate, 'price': info['rate']}
        if effective_sell_rate > best_sell['effective_rate']:
            best_sell = {'exchange': exchange, 'effective_rate': effective_sell_rate, 'price': info['rate']}

    potential_profit = best_sell['effective_rate'] - best_buy['effective_rate']

    if potential_profit > 0:
        print(f"Arbitrage Opportunity: Buy on {best_buy['exchange']} at ${best_buy['effective_rate']} and sell on {best_sell['exchange']} at ${best_sell['effective_rate']}. Potential profit: ${potential_profit} per BTC")
        # TODO: update order_amount, ensure this is appropriate
        order_amount = 0.01  # BTC
        place_order(best_buy['exchange'], 'buy', order_amount, best_buy['price'])
        place_order(best_sell['exchange'], 'sell', order_amount, best_sell['price'])
    else:
        print("No arbitrage opportunities found.")

async def main():
    prices = await fetch_prices()
    find_arbitrage_opportunities(prices)
    await close_exchanges()

# Run the async main function
asyncio.run(main())
