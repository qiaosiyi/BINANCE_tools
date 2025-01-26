#!/bin/bash
#!/usr/bin/env bash
"""
功能：统计当前目录下所有.db文件的基本信息
用途：快速了解数据库文件的状态和内容
用法：
1. 将脚本放在与.db文件相同目录下
2. 直接运行脚本: ./dbinfo.sh
3. 脚本会自动分析当前目录下所有.db文件
4. 输出信息包括:
   - 文件大小
   - 创建时间
   - 最后修改时间
   - 记录数量
   - 最早记录时间
   - 最新记录时间
"""

echo "数据库信息统计:"
echo "----------------------------------------"

for db in *.db; do
    if [ -f "$db" ]; then
        echo "数据库文件: $db"
        echo "文件大小: $(du -h "$db" | cut -f1)"
        echo "创建时间: $(stat -c %w "$db")"
        echo "最后修改时间: $(stat -c %y "$db")"
        
        # 使用sqlite3统计记录数
        count=$(sqlite3 "$db" "SELECT COUNT(*) FROM klines;")
        echo "记录数量: $count"
        
        # 获取最早和最新的记录时间
        first_record=$(sqlite3 "$db" "SELECT datetime(close_time/1000, 'unixepoch', 'localtime') FROM klines ORDER BY close_time ASC LIMIT 1;")
        last_record=$(sqlite3 "$db" "SELECT datetime(close_time/1000, 'unixepoch', 'localtime') FROM klines ORDER BY close_time DESC LIMIT 1;")
        
        echo "最早记录时间: $first_record"
        echo "最新记录时间: $last_record"
        echo "----------------------------------------"
    fi
done
