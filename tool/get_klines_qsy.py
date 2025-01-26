#!/usr/bin/env python3
"""
功能：获取币安交易所指定交易对的K线数据并保存到SQLite数据库
用途：收集和存储加密货币交易数据用于分析
用法：
1. 运行脚本时需要提供两个参数:
   - 第一个参数是交易对名称,如 btcusdt
   - 第二个参数是运行时间(秒),如 3600
   示例: ./get_klines_qsy.py btcusdt 3600
2. 脚本会创建一个以交易对命名的SQLite数据库文件
3. 数据库表结构:
   - close_time: K线收盘时间戳(毫秒)
   - close_price: 收盘价
   - volume: 交易量
   - quote_volume: 计价货币交易量
"""

import logging
import time
from datetime import datetime, timedelta
from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient
import sys
import sqlite3 

if len(sys.argv) < 3:
    print("请在运行脚本时提供交易对参数和运行时间(秒)")
    sys.exit(1)
symbol_name = sys.argv[1].upper()
run_time = int(sys.argv[2])

def init_db(symbol_name):
    dbname = f"{symbol_name}_klines.db"
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS klines (
            close_time INTEGER PRIMARY KEY,
            close_price REAL,
            volume REAL,
            quote_volume REAL
        )
    ''')
    db.commit()
    return db


# result(data structure): [
#     1499040000000,      // Kline open time
#     "0.01634790",       // Open price
#     "0.80000000",       // High price
#     "0.01575800",       // Low price
#     "0.01577100",       // Close price
#     "148976.11427815",  // Volume
#     1499644799999,      // Kline Close time
#     "2434.19055334",    // Quote asset volume
#     308,                // Number of trades
#     "1756.87402397",    // Taker buy base asset volume
#     "28.46694368",      // Taker buy quote asset volume
#     "0"                 // Unused field, ignore.
#   ]

result = None
def on_close(_):
    pass
    logging.info("Do custom stuff when connection is closed")


def message_handler(_, message):
    logging.info(message)
    # print("message: ", message)
    if isinstance(message, str):
        message = eval(message)
    if isinstance(message, dict) and 'result' in message:
        global result
        result = message['result']

def print_utc8_time(open_time):
    utc_time = datetime.fromtimestamp(open_time/1000)  # Convert milliseconds to seconds
    utc8_time = utc_time + timedelta(hours=0)  # UTC+8
    print(f"UTC+8 Time: {utc8_time.year}-{utc8_time.month:02d}-{utc8_time.day:02d} {utc8_time.hour:02d}:{utc8_time.minute:02d}:{utc8_time.second:02d}.{utc8_time.microsecond//1000:03d}")

def result_handler(result):
    if result is None or len(result) == 0:
        print("No data")
        print(result)
        return
        
    for kline in result:
        open_time = kline[0]
        open_price = float(kline[1])
        high_price = float(kline[2]) 
        low_price = float(kline[3])
        close_price = float(kline[4])
        volume = float(kline[5])
        close_time = kline[6]
        quote_volume = float(kline[7])
        trades_count = kline[8]
        taker_buy_volume = float(kline[9])
        taker_buy_quote_volume = float(kline[10])
        
#         print(f"""
# Kline Data:
# Open Time: {(open_time)}
# Open Price: {open_price}
# High Price: {high_price}
# Low Price: {low_price} 
# Close Price: {close_price}
# Volume: {volume}
# Close Time: {(close_time)}
# Quote Volume: {quote_volume}
# Number of Trades: {trades_count}
# Taker Buy Volume: {taker_buy_volume}
# Taker Buy Quote Volume: {taker_buy_quote_volume}
#         """)
        # Store data in database using integer and float types to minimize storage
        # 先检查是否已存在相同的 close_time


        

        db.execute("""
            INSERT INTO klines (close_time, close_price, volume, quote_volume) 
            VALUES (?, ?, ?, ?)
        """, (
            int(close_time),  # timestamp as integer
            float(close_price), # price as float 
            float(volume), # volume as float
            float(quote_volume) # quote volume as float
        ))

        db.commit()
        # print_utc8_time(open_time)
        # print_utc8_time(close_time)
    
def get_klines_qsy(symbol, interval, **params):
    config_logging(logging, logging.ERROR)
    # config_logging(logging, logging.INFO)   
    global db
    db = init_db(symbol_name)
    my_client = SpotWebsocketAPIClient(on_message=message_handler, on_close=on_close)

    count = 0
    close_time_last = 0
    while True:
        try:
            start_time = time.time()
            
            my_client.klines(symbol, interval, **params)
            time.sleep(0.3)

            close_time_now = result[0][6]
            if close_time_now == close_time_last:
                continue
            else:
                pass
                # print(f"开始第{count+1}次循环, 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}, 时间戳: {(start_time)}")
            close_time_last = close_time_now
            result_handler(result)
            count += 1
            while (time.time() - start_time) < 1:
                time.sleep(0.1)
            if count == run_time:
                print(f"已运行{run_time}次,程序结束")
                break
        # 检查是否达到运行时间限制
            if time.time() - start_time >= run_time:
                print(f"已运行{run_time}秒,程序结束")
                break
        
        except Exception as e:
            print(e)
            break
        

    logging.info("closing ws connection")
    
    my_client.stop()    
    db.close()
    pass

get_klines_qsy(symbol_name, "1s", limit=1)