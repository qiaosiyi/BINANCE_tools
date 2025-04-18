#! /usr/bin/env python3

import logging
import json
from binance.spot import Spot
from binance.lib.utils import config_logging

config_logging(logging, logging.ERROR)

client = Spot()
logging.info(client.time())

with open('config.json', 'r') as f:
    config = json.load(f)
api_key = config['api_key']
api_secret = config['api_secret']
client = Spot(api_key=api_key, api_secret=api_secret)

# 从命令行获取交易对参数
import sys

if len(sys.argv) == 2:
    symbol = sys.argv[1].upper()
else:
    symbol = input("Enter the trading pair symbol (e.g., BTCUSDT): ").upper()
logging.info(client.account())

# Post a new order
params = {
    'symbol': symbol,
}

response = client.cancel_open_orders(**params)
logging.info(response)