#!/usr/bin/env python3
import json,datetime
import logging
from binance.spot import Spot
from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient
import subprocess
import sys

def get_current_price(symbol):
    try:
        # 调用 price.py 脚本并获取输出
        result = subprocess.run(['python3', 'price.py', symbol], 
                              capture_output=True, 
                              text=True,
                              check=True)
        # 返回输出结果(当前价格)
        return float(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"获取价格时发生错误: {e}")
        sys.exit(1)


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
    elif 'SCR' in symbol:
        return f"{quantity:.1f}"
    else:
        "No Symbol Type"


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
    elif 'SCR' in symbol:
        return f"{price:.3f}"
    else:
        "No Symbol Type"


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

def get_balance():
    client = Spot()
    logging.info(client.time())
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    api_key = config['api_key']
    api_secret = config['api_secret']
    client = Spot(api_key=api_key, api_secret=api_secret)
    account_info = client.account()

    return account_info


def create_orders(symbol, side, base_price, price_range, num_orders, quantity):
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
            if side == "BUY":
                target_quantity_step = gen_target_quantity_step(symbol, quantity_step/float(price))
                str_quantity_step = f"{quantity_step:.1f}"
                orders.append({"symbol": symbol, "side": side, "price": str_price, "quantity": target_quantity_step, "USD": str_quantity_step})
            else:
                target_quantity_step = gen_target_quantity_step(symbol, quantity_step)
                str_quantity_step = f"{quantity_step*float(price):.1f}"
                orders.append({"symbol": symbol, "side": side, "price": str_price, "quantity": target_quantity_step, "USD": str_quantity_step})
            
        elif price_step < 0:
            price = gen_price(symbol,base_price + (i + 1) * price_step)
            str_price = str(price)
            if side == "BUY":
                target_quantity_step = gen_target_quantity_step(symbol, quantity_step/float(price))
                str_quantity_step = f"{quantity_step:.1f}"
                orders.append({"symbol": symbol, "side": side, "price": str_price, "quantity": target_quantity_step, "USD": str_quantity_step})
            else:
                print("sorry no way! price range should be positive!")
                exit()
    
    return orders


target_coin = input("Enter the trading target coin (e.g., BTC): ").upper()
target_coins = ['ADA', 'BNB', 'ETH', 'BTC', 'DOGE', 'SCR']
while True:
    if target_coin not in target_coins:
        print(f"错误: 请选择有效的交易币种 ({'/'.join(target_coins)})")
        target_coin = input("请重新输入交易币种 (e.g., BTC): ").upper()
    else:
        break


stable_coins = ['USDT', 'USDC', 'FDUSD']
# 遍历所有稳定币,查询每个交易对的价格
print("\n当前价格:")

print("-" * 25)
print(f"{'交易对':<15}{'价格':<10}")
print("-" * 25)
for stable_coin in stable_coins:
    symbol = target_coin + stable_coin
    try:
        price = get_current_price(symbol)
        print(f"{symbol:<15}{price:<10.4f}")
    except:
        print(f"{symbol:<15}{'无法获取':<10}")
print("-" * 25)
balance = get_balance()['balances']
print("\nYour Account Balance:")
print("-" * 40)
print(f"{'Asset':<10}{'Free':<15}{'Locked':<15}")
print("-" * 40)
for asset in balance:
    if (float(asset['free']) > 0 or float(asset['locked']) > 0) and asset['asset'] in ['USDT', 'USDC', 'FDUSD']:
        print(f"{asset['asset']:<10}{float(asset['free']):<15.3f}{float(asset['locked']):<15.3f}")
print("-" * 40)
for asset in balance:
    if (float(asset['free']) > 0 or float(asset['locked']) > 0) and asset['asset'] in [target_coin]:
        print(f"{asset['asset']:<10}{float(asset['free']):<15.3f}{float(asset['locked']):<15.3f}")
print("-" * 40)

# 让用户选择稳定币
while True:
    stable_coin = input(f"\n请选择稳定币 ({'/'.join(stable_coins)})default USDT: ").upper()
    if stable_coin in stable_coins or \
       (stable_coin.upper() == 'T' and 'USDT' in stable_coins) or \
       (stable_coin.upper() == 'F' and 'FDUSD' in stable_coins) or \
       (stable_coin.upper() == 'C' and 'USDC' in stable_coins):
        if stable_coin.upper() == 'T':
            stable_coin = 'USDT'
        elif stable_coin.upper() == 'F':
            stable_coin = 'FDUSD'
        elif stable_coin.upper() == 'C':
            stable_coin = 'USDC'
        else:
            stable_coin = 'USDT'
        break
    else:
        stable_coin = 'USDT'
        break



symbol=target_coin+stable_coin


price_choice = input("Do you want to use current market price as base price? (default current price / N): ").upper()
if price_choice == 'N':
    base_price = float(input("Please enter your base price: "))
    print(symbol, "base_price: ", base_price)
elif price_choice == 'Y':
    base_price = get_current_price(symbol)
    print(symbol, "base price: ", base_price,"(you chose current price)")
elif not price_choice:
    price_choice = 'Y'
    base_price = get_current_price(symbol)
    print(symbol, "base price: ", base_price)



price_range = input("Enter the price range (can be a number or percentage, e.g., 10 or 10%): default -10%: ")
if '%' in price_range:
    price_range = price_range.strip('%')
    if price_range.startswith('-'):
        price_range = - float(price_range.lstrip('-')) / 100 
    else:
        price_range = float(price_range) / 100
else:
    price_range = float(-0.1)


side = input("Enter the trading side (B for BUY, S for SELL): default BUY: ")
if side.upper() == 'B':
    side = 'BUY'
elif side.upper() == 'S':
    side = 'SELL'
else:
    side = 'BUY'
num_orders = input("Enter the number of orders: default 30: ")
if not num_orders:
    num_orders = 30
else:
    num_orders = int(num_orders)



if side == 'BUY':
    
    quantity = (input("Enter the total trading quantity in "+stable_coin+": default 500: "))
    if not quantity:
        quantity = 500
else:
    quantity = float(input("Enter the total trading quantity in "+target_coin+": "))

gen_orders = create_orders(symbol, side, base_price, price_range, num_orders, quantity)

with open('order_log.txt', 'a') as f:
    f.write(f"\nOrder Details ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n")
    f.write(f"{'No.':<6}{'Symbol':<12}{'Side':<6}{'Price':<12}{'Quantity':<12}{'USD':<10}\n")
    f.write("-" * 60 + "\n")
    for i, order in enumerate(gen_orders, 1):
        f.write(f"{i:<6}{order['symbol']:<12}{order['side']:<6}{order['price']:<12}{order['quantity']:<12}{order['USD']:<10}")
        f.write("\n")
    f.write("-" * 60)
    
print("\nOrder Details:")
print(f"{'No.':<6}{'Symbol':<12}{'Side':<6}{'Price':<12}{'Quantity':<12}{'USD':<10}")
print("-" * 60)

for i, order in enumerate(gen_orders, 1):
    print(f"{i:<6}{order['symbol']:<12}{order['side']:<6}{order['price']:<12}{order['quantity']:<12}{order['USD']:<10}")
print("-" * 60)

# Ask user whether to execute orders
user_input = input("Execute orders? (default Y/N): ")
with open('order_log.txt', 'a') as f:

    if user_input.upper() == 'Y':
        run_orders(gen_orders)
        print("Orders executed")    
        f.write("Orders executed\n")
    elif user_input.upper() == 'N':
        print("Order execution cancelled")
        f.write("Order execution cancelled\n")
    else:
        run_orders(gen_orders)
        print("Orders executed")
        f.write("Orders executed\n")



