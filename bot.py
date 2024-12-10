import asyncio
import ccxt.async_support as ccxt
import math

from config import (
    COINBASEPRO_API_KEY,
    COINBASEPRO_SECRET,
    KRAKEN_API_KEY,
    KRAKEN_SECRET,
)

# Initialize exchanges with ccxt.async_support and API credentials
exchanges = {
    "coinbasepro": ccxt.coinbasepro(
        {"apiKey": COINBASEPRO_API_KEY, "secret": COINBASEPRO_SECRET}
    ),
    "kraken": ccxt.kraken({"apiKey": KRAKEN_API_KEY, "secret": KRAKEN_SECRET}),
}

exchanges_fees = {
    "bitstamp": {"trading_fee": 0.25, "withdrawal_fee": 5.00},
    "coinbasepro": {"trading_fee": 0.50, "withdrawal_fee": 2.50},
    "kraken": {"trading_fee": 0.26, "withdrawal_fee": 0.00},
}


async def fetch_ticker(exchange, symbol="BTC/USD"):
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
        task = fetch_ticker(exchange, "BTC/USD")
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    for exchange_id, ticker in results:
        if ticker:
            last_price = ticker["last"]
            prices[exchange_id] = {
                "rate": last_price,
                **exchanges_fees.get(exchange_id, {}),
            }
            print(f"Price for {exchange_id}: {last_price}")

    print("Finished fetching prices.")
    return prices


async def place_order(exchange_id, side, amount, symbol="BTC/USD"):
    exchange = exchanges[exchange_id]
    print(
        f"Attempting to place a {side} order for {amount} of {symbol} on {exchange_id}..."
    )

    try:
        if side == "buy":
            order = await exchange.create_market_buy_order(symbol, amount)
        elif side == "sell":
            order = await exchange.create_market_sell_order(symbol, amount)

        print(f"Order placed on {exchange_id}: {order}")
    except Exception as e:
        print(f"Failed to place order on {exchange_id}: {e}")


def build_graph(prices):
    graph = {}
    for src in prices:
        graph[src] = {}
        for dst in prices:
            if src != dst:
                rate = prices[dst]["rate"] / prices[src]["rate"]
                fee = (1 + prices[src]["trading_fee"] / 100) * (
                    1 - prices[dst]["trading_fee"] / 100
                ) - prices[src]["withdrawal_fee"] / prices[src]["rate"]
                graph[src][dst] = -math.log(rate * fee)
    return graph


def bellman_ford(graph, start):
    # 1) Initialize distances from start to all other nodes as INFINITE
    distance = {node: float("inf") for node in graph}
    predecessor = {node: None for node in graph}
    distance[start] = 0

    # 2) Relax all edges |V| - 1 times.
    for _ in range(len(graph) - 1):
        for u in graph:
            for v in graph[u]:
                if distance[u] + graph[u][v] < distance[v]:
                    distance[v] = distance[u] + graph[u][v]
                    predecessor[v] = u

    # 3) Check for negative-weight cycles.
    for u in graph:
        for v in graph[u]:
            if distance[u] + graph[u][v] < distance[v]:
                # Negative cycle detected, reconstruct cycle
                arbitrage_opportunity = []
                current = v
                while True:
                    arbitrage_opportunity.append(current)
                    current = predecessor[current]
                    if current == v and len(arbitrage_opportunity) > 1:
                        arbitrage_opportunity.append(current)
                        break
                arbitrage_opportunity.reverse()
                return arbitrage_opportunity

    return None


async def find_arbitrage_opportunities(prices):
    print("Analyzing arbitrage opportunities...")
    graph = build_graph(prices)
    start_node = next(iter(graph))  # Start with any node

    arbitrage_opportunity = bellman_ford(graph, start_node)
    if arbitrage_opportunity:
        print(f"Arbitrage Opportunity Detected: {arbitrage_opportunity}")
        # Place orders
        order_amount = 0.01  # BTC
        for i in range(len(arbitrage_opportunity) - 1):
            await place_order(arbitrage_opportunity[i], "buy", order_amount)
            await place_order(arbitrage_opportunity[i + 1], "sell", order_amount)
    else:
        print("No arbitrage opportunities found.")


async def main():
    print("Starting arbitrage bot...")
    try:
        while True:
            prices = await fetch_prices()
            await find_arbitrage_opportunities(prices)
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        print("Closing exchanges...")
        await asyncio.gather(*(exchange.close() for exchange in exchanges.values()))
        print("Execution completed.")


asyncio.run(main())
