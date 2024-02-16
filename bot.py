from config import COINAPI_KEY
import requests

API_KEY = COINAPI_KEY
# TODO: double check these fee percentages
exchanges_fees = {
    'BITSTAMP': {'trading_fee': 0.25, 'withdrawal_fee': 5.00},
    'COINBASE': {'trading_fee': 0.50, 'withdrawal_fee': 2.50},
    'KRAKEN': {'trading_fee': 0.26, 'withdrawal_fee': 0.00},
}
headers = {'X-CoinAPI-Key': API_KEY}
prices = {}

# Fetch BTC prices from each exchange
for exchange in exchanges_fees.keys():
    url = f'https://rest.coinapi.io/v1/exchangerate/BTC/USD?exchange={exchange}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        prices[exchange] = {'rate': data['rate'], **exchanges_fees[exchange]}
    else:
        print(f"Failed to fetch data for {exchange}")

# def place_order(exchange, order_type, amount, price):
#     # Place an order via CoinAPI EMS
#     # TODO DOUBLE CHECK EMS DOCUMENTATION
#     url = f"https://ems.coinapi.io/api/v1/orders/place"
#     data = {
#         "exchange_id": exchange,
#         "symbol_id": "BTC/USD",
#         "order_type": order_type,
#         "quantity": amount,
#         "price": price,
#         # Additional required fields ..
#     }
#     response = requests.post(url, headers=headers, json=data)
#     return response.json()

def find_arbitrage_opportunities(prices):
    best_buy = {'exchange': None, 'effective_rate': float('inf')}
    best_sell = {'exchange': None, 'effective_rate': 0}

    # Calculate effective buy and sell rates considering fees
    for exchange, info in prices.items():
        effective_buy_rate = info['rate'] * (1 + info['trading_fee'] / 100)
        effective_sell_rate = (info['rate'] * (1 - info['trading_fee'] / 100)) - info['withdrawal_fee']

        # Update best buy and sell rates
        if effective_buy_rate < best_buy['effective_rate']:
            best_buy = {'exchange': exchange, 'effective_rate': effective_buy_rate}
        if effective_sell_rate > best_sell['effective_rate']:
            best_sell = {'exchange': exchange, 'effective_rate': effective_sell_rate}

    potential_profit = best_sell['effective_rate'] - best_buy['effective_rate']

    if potential_profit > 0:
        print(f"Arbitrage Opportunity: Buy on {best_buy['exchange']} at ${best_buy['effective_rate']} and sell on {best_sell['exchange']} at ${best_sell['effective_rate']}. Potential profit: ${potential_profit} per BTC")
        # Order placement
        # buy_response = place_order(best_buy['exchange'], "buy", 1, best_buy['effective_rate'])
        # sell_response = place_order(best_sell['exchange'], "sell", 1, best_sell['effective_rate'])
        # print(f"Buy Order Response: {buy_response}")
        # print(f"Sell Order Response: {sell_response}")
    else:
        print("No arbitrage opportunities found.")

find_arbitrage_opportunities(prices)
