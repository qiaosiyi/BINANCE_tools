#!/usr/bin/env python

import logging
import time
from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient
import sys


if len(sys.argv) < 2:
    print("请在运行脚本时提供交易对参数")
    sys.exit(1)
symbol = sys.argv[1].upper()



config_logging(logging, logging.ERROR)

price = None
def on_close(_):
    pass
    logging.info("Do custom stuff when connection is closed")


def message_handler(_, message):
    # logging.info(message)
    # print("message: ", message)
    if isinstance(message, str):
        message = eval(message)
    if isinstance(message, dict) and 'result' in message:
        global price
        price = message['result']['price']
    
my_client = SpotWebsocketAPIClient(on_message=message_handler, on_close=on_close)

# time.sleep(1)
my_client.ticker_price(symbol=symbol)
time.sleep(0.1)


logging.info("closing ws connection")
print(price)
my_client.stop()