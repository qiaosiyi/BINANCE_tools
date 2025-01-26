#!/usr/bin/env python3
"""
功能：分析数据库中k线数据的时间戳间隔
用途：检查k线数据的连续性和完整性
用法：
1. 将脚本放在与.db文件相同目录下
2. 直接运行脚本: ./analys_db.py
3. 脚本会自动分析当前目录下所有.db文件
4. 输出分析结果包括:
   - 时间戳总数
   - 大于1000毫秒的时间差数量
   - 等于1000毫秒的时间差数量 
   - 最大时间差及其出现次数
"""

import sqlite3
import os
from datetime import datetime

def analyze_timestamp_gaps(db_path):
    print(f"\n分析数据库: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有时间戳并排序
    cursor.execute("SELECT close_time FROM klines ORDER BY close_time")
    timestamps = [row[0] for row in cursor.fetchall()]
    print(f"时间戳列表长度: {len(timestamps)}")
    
    gaps = 0
    exact_1000ms = 0
    max_diff = 0
    max_diff_count = 0
    
    for i in range(len(timestamps)-1):
        diff = timestamps[i+1] - timestamps[i]
        if diff > 1000:  # 大于1000毫秒
            gaps += 1
            if diff > max_diff:
                max_diff = diff
                max_diff_count = 1
            elif diff == max_diff:
                max_diff_count += 1
        elif diff == 1000:  # 等于1000毫秒
            exact_1000ms += 1
    
    if gaps == 0:
        print("未发现大于999毫秒的时间差")
    else:
        print(f"总共发现 {gaps} 处大于1000毫秒的时间差")
        print(f"发现 {exact_1000ms} 处等于1000毫秒的时间差")
        print(f"最大时间差为 {max_diff/1000:.2f} 秒，出现了 {max_diff_count} 次")
    
    conn.close()

def main():
    # 获取当前目录下所有的.db文件
    db_files = [f for f in os.listdir('.') if f.endswith('.db')]
    
    if not db_files:
        print("当前目录下没有找到.db文件")
        return
        
    for db_file in db_files:
        analyze_timestamp_gaps(db_file)

if __name__ == "__main__":
    main()
