from config import COINAPI_KEY

import requests

API_KEY = COINAPI_KEY
# List of exchanges to fetch BTC prices from
exchanges = ['BITSTAMP', 'COINBASE', 'KRAKEN']
# Headers for the API request
headers = {'X-CoinAPI-Key': API_KEY}
# Dictionary to store prices
prices = {}

# Fetch BTC prices from each exchange
for exchange in exchanges:
    url = f'https://rest.coinapi.io/v1/exchangerate/BTC/USD?exchange={exchange}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        prices[exchange] = data['rate']
    else:
        print(f"Failed to fetch data for {exchange}")

def find_arbitrage_opportunities(prices):
    buy_exchange, buy_price = min(prices.items(), key=lambda x: x[1])
    sell_exchange, sell_price = max(prices.items(), key=lambda x: x[1])
    profit = sell_price - buy_price
    
    if profit > 0:
        print(f"Arbitrage Opportunity: Buy on {buy_exchange} at ${buy_price} and sell on {sell_exchange} at ${sell_price}. Potential profit: ${profit} per BTC")
    else:
        print("No arbitrage opportunities found.")

find_arbitrage_opportunities(prices)

