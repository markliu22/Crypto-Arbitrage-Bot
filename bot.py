import asyncio
import ccxt.async_support as ccxt  # Use async_support for asynchronous operations

from config import (BITSTAMP_API_KEY, BITSTAMP_SECRET, COINBASEPRO_API_KEY, 
                    COINBASEPRO_SECRET, KRAKEN_API_KEY, KRAKEN_SECRET)

# Initialize exchanges with ccxt.async_support and API credentials
exchanges = {
    'coinbasepro': ccxt.coinbasepro({'apiKey': COINBASEPRO_API_KEY, 'secret': COINBASEPRO_SECRET}),
    'kraken': ccxt.kraken({'apiKey': KRAKEN_API_KEY, 'secret': KRAKEN_SECRET}),
}

# Adjusted for demonstration; ensure these are correct and include other necessary parameters for your accounts.
exchanges_fees = {
    'bitstamp': {'trading_fee': 0.25, 'withdrawal_fee': 5.00},
    'coinbasepro': {'trading_fee': 0.50, 'withdrawal_fee': 2.50},
    'kraken': {'trading_fee': 0.26, 'withdrawal_fee': 0.00},
}

async def fetch_ticker(exchange, symbol='BTC/USD'):
    print(f"Fetching ticker for {symbol} from {exchange.id}...")
    try:
        ticker = await exchange.fetch_ticker(symbol)
        print(f"Successfully fetched ticker from {exchange.id}.")
        return exchange.id, ticker
    except Exception as e:
        print(f"Failed to fetch data for {exchange.id}: {e}")
        return exchange.id, None

async def fetch_prices():
    print("Starting to fetch prices...")
    prices = {}
    tasks = []

    for exchange_id, exchange in exchanges.items():
        task = fetch_ticker(exchange, 'BTC/USD')
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)

    for exchange_id, ticker in results:
        if ticker:
            last_price = ticker['last']
            prices[exchange_id] = {'rate': last_price, **exchanges_fees.get(exchange_id, {})}
            print(f"Price for {exchange_id}: {last_price}")
    
    print("Finished fetching prices.")
    return prices

# TODO
def place_order(exchange_id, side, amount, price):
    # This function needs to be called within an asyncio event loop if using async exchange instances
    # For demonstration purposes, we're assuming synchronous execution for order placement
    print(f"Placing order on {exchange_id}: {side} {amount} @ {price}")

def find_arbitrage_opportunities(prices):
    print("Analyzing arbitrage opportunities...")
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
        # Note: Actual order placement logic should be implemented here
        # place_order(best_buy['exchange'], 'buy', order_amount, best_buy['price'])
        # place_order(best_sell['exchange'], 'sell', order_amount, best_sell['price'])
    else:
        print("No arbitrage opportunities found.")

async def main():
    print("Starting arbitrage bot...")
    # ref for ASCII art: https://patorjk.com/software/taag/#p=display&f=Bloody&t=by%20mork%20lau
    print("""
 ▄▄▄▄ ▓██   ██▓    ███▄ ▄███▓ ▒█████   ██▀███   ██ ▄█▀    ██▓    ▄▄▄       █    ██ 
▓█████▄▒██  ██▒   ▓██▒▀█▀ ██▒▒██▒  ██▒▓██ ▒ ██▒ ██▄█▒    ▓██▒   ▒████▄     ██  ▓██▒
▒██▒ ▄██▒██ ██░   ▓██    ▓██░▒██░  ██▒▓██ ░▄█ ▒▓███▄░    ▒██░   ▒██  ▀█▄  ▓██  ▒██░
▒██░█▀  ░ ▐██▓░   ▒██    ▒██ ▒██   ██░▒██▀▀█▄  ▓██ █▄    ▒██░   ░██▄▄▄▄██ ▓▓█  ░██░
░▓█  ▀█▓░ ██▒▓░   ▒██▒   ░██▒░ ████▓▒░░██▓ ▒██▒▒██▒ █▄   ░██████▒▓█   ▓██▒▒▒█████▓ 
░▒▓███▀▒ ██▒▒▒    ░ ▒░   ░  ░░ ▒░▒░▒░ ░ ▒▓ ░▒▓░▒ ▒▒ ▓▒   ░ ▒░▓  ░▒▒   ▓▒█░░▒▓▒ ▒ ▒ 
▒░▒   ░▓██ ░▒░    ░  ░      ░  ░ ▒ ▒░   ░▒ ░ ▒░░ ░▒ ▒░   ░ ░ ▒  ░ ▒   ▒▒ ░░░▒░ ░ ░ 
 ░    ░▒ ▒ ░░     ░      ░   ░ ░ ░ ▒    ░░   ░ ░ ░░ ░      ░ ░    ░   ▒    ░░░ ░ ░ 
 ░     ░ ░               ░       ░ ░     ░     ░  ░          ░  ░     ░  ░   ░     
      ░░ ░                                                                         
""")
    prices = await fetch_prices()
    find_arbitrage_opportunities(prices)
    print("Closing exchanges...")
    await asyncio.gather(*(exchange.close() for exchange in exchanges.values()))
    print("Bot execution completed.")

# Run the async main function
asyncio.run(main())
