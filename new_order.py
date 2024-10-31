#!/usr/bin/env python3
import json
import logging
from binance.spot import Spot
from binance.lib.utils import config_logging

config_logging(logging, logging.ERROR)

def gen_target_quantity_step(symbol,quantity):
    if 'BTC' in symbol:
        return f"{quantity:.5f}"
    elif 'ETH' in symbol:
        return f"{quantity:.4f}"
    elif 'ADA' in symbol:
        return f"{quantity:.1f}"
    elif 'BNB' in symbol:
        return f"{quantity:.3f}"
    elif 'DOGE' in symbol:
        return f"{int(quantity)}"

def gen_price(symbol,price):
    if 'BTC' in symbol:
        return f"{price:.2f}"
    elif 'ETH' in symbol:
        return f"{price:.2f}"
    elif 'ADA' in symbol:
        return f"{price:.4f}"
    elif 'BNB' in symbol:
        return f"{price:.1f}"
    elif 'DOGE' in symbol:
        return f"{price:.5f}"


def buy_order(client, symbol, quantity, price):
    # Post a new order
    params = {
    'symbol': symbol,
    'side': 'BUY',
    'type': 'LIMIT',
    'timeInForce': 'GTC',
    'quantity': quantity,
    'price': price
    }

    response = client.new_order(**params)
    logging.info(response)


def sell_order(client, symbol, quantity, price):
    # Post a new order
    params = {
    'symbol': symbol,
    'side': 'SELL',
    'type': 'LIMIT',
    'timeInForce': 'GTC',
    'quantity': quantity,
    'price': price
    }

    response = client.new_order(**params)
    logging.info(response)

def run_orders(orders):
    client = Spot()
    logging.info(client.time())
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    api_key = config['api_key']
    api_secret = config['api_secret']
    client = Spot(api_key=api_key, api_secret=api_secret)

    logging.info(client.account())

    for order in orders:
        if order['side'] == 'BUY':
            logging.info(f"BUY {order['symbol']} {order['quantity']} {order['price']}") 
            buy_order(client, order['symbol'], order['quantity'], order['price'])
        else:
            logging.info(f"SELL {order['symbol']} {order['quantity']} {order['price']}")
            sell_order(client, order['symbol'], order['quantity'], order['price'])


def create_orders(symbol, side, base_price, price_range, num_orders, quantity):
    print("price_range_a: ", price_range)

    orders = []
    if isinstance(price_range, str) and '%' in price_range:
        price_range_str = price_range.strip('%')
        if price_range_str.startswith('-'):
            price_range = -float(price_range_str[1:])  * base_price
        else:
            price_range = float(price_range_str)  * base_price
    elif isinstance(price_range, (int, float)):
        price_range = price_range * base_price

    price_step = (price_range ) / (num_orders)
    quantity_step = quantity / num_orders

    for i in range(num_orders):
        if price_step > 0:
            price = gen_price(symbol,base_price + (i + 1) * price_step)
            str_price = str(price)
            target_quantity_step = gen_target_quantity_step(symbol, quantity_step/float(price))
            str_quantity_step = f"{quantity_step:.1f}"
            orders.append({"symbol": symbol, "side": side, "price": str_price, "quantity": target_quantity_step, "USD": str_quantity_step})
        elif price_step < 0:
            price = gen_price(symbol,base_price + (i + 1) * price_step)
            str_price = str(price)
            target_quantity_step = gen_target_quantity_step(symbol, quantity_step/float(price))
            str_quantity_step = f"{quantity_step:.1f}"
            orders.append({"symbol": symbol, "side": side, "price": str_price, "quantity": target_quantity_step, "USD": str_quantity_step})
    
    return orders


symbol = input("Enter the trading pair symbol (e.g., BTCUSDT): ").upper()
base_price = float(input("Enter the base price: "))
price_range = input("Enter the price range (can be a number or percentage, e.g., 10 or 10%): ")
if '%' in price_range:
    price_range = price_range.strip('%')
    if price_range.startswith('-'):
        price_range = - float(price_range.lstrip('-')) / 100 
    else:
        price_range = float(price_range) / 100
else:
    price_range = float(price_range)
side = input("Enter the trading side (B for BUY, S for SELL): ")
if side.upper() == 'B':
    side = 'BUY'
elif side.upper() == 'S':
    side = 'SELL'
else:
    raise ValueError("Invalid trading side, please enter B or S")
num_orders = int(input("Enter the number of orders: "))
quantity = float(input("Enter the total trading quantity in USD: "))
gen_orders = create_orders(symbol, side, base_price, price_range, num_orders, quantity)

print(gen_orders)

# Ask user whether to execute orders
user_input = input("Execute orders? (Y/N): ")

if user_input.upper() == 'Y':
    run_orders(gen_orders)
    print("Orders executed")
elif user_input.upper() == 'N':
    print("Order execution cancelled")
else:
    print("Invalid input, order execution cancelled")