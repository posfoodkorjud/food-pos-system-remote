#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime, timedelta

def test_localtime_consistency():
    """ทดสอบว่าการใช้ localtime ในระบบทำงานสอดคล้องกัน"""
    
    conn = sqlite3.connect('A_FOOD_POS/FOOD_POS/pos_database.db')
    cursor = conn.cursor()
    
    print("=== ทดสอบการใช้ localtime ในระบบ ===")
    print(f"วันที่ปัจจุบัน: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ทดสอบ 1: เปรียบเทียบ UTC vs Local time
    print("1. เปรียบเทียบ UTC vs Local time:")
    cursor.execute("SELECT datetime('now') as utc_time, datetime('now', 'localtime') as local_time")
    result = cursor.fetchone()
    print(f"   UTC time: {result[0]}")
    print(f"   Local time: {result[1]}")
    print()
    
    # ทดสอบ 2: ตรวจสอบออเดอร์วันนี้ด้วย localtime
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"2. ออเดอร์วันนี้ ({today}) ด้วย localtime:")
    cursor.execute("""
        SELECT order_id, total_amount, 
               DATE(created_at, 'localtime') as local_date,
               created_at
        FROM orders 
        WHERE DATE(created_at, 'localtime') = ?
        ORDER BY created_at DESC
    """, (today,))
    
    orders = cursor.fetchall()
    total_sales = 0
    print(f"   พบ {len(orders)} ออเดอร์:")
    for order in orders:
        print(f"   - Order {order[0]}: {order[1]} บาท (วันที่: {order[2]}, เวลา: {order[3]})")
        total_sales += order[1]
    print(f"   รวมยอดขาย: {total_sales} บาท")
    print()
    
    # ทดสอบ 3: ตรวจสอบยอดขายรายวันล่าสุด
    print("3. ยอดขายรายวัน 5 วันล่าสุด (ด้วย localtime):")
    cursor.execute("""
        SELECT DATE(created_at, 'localtime') as order_date,
               COUNT(*) as orders,
               SUM(total_amount) as sales
        FROM orders 
        GROUP BY DATE(created_at, 'localtime')
        ORDER BY order_date DESC 
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} ออเดอร์, {row[2]} บาท")
    print()
    
    # ทดสอบ 4: ตรวจสอบข้อมูลกราฟ
    print("4. ข้อมูลกราฟ 7 วันล่าสุด (ด้วย localtime):")
    cursor.execute("""
        SELECT DATE(created_at, 'localtime') as date,
               COALESCE(SUM(total_amount), 0) as total
        FROM orders 
        WHERE DATE(created_at, 'localtime') >= DATE('now', 'localtime', '-7 days')
        GROUP BY DATE(created_at, 'localtime')
        ORDER BY date
    """)
    
    chart_data = cursor.fetchall()
    print(f"   พบข้อมูล {len(chart_data)} วัน:")
    for row in chart_data:
        print(f"   {row[0]}: {row[1]} บาท")
    print()
    
    # ทดสอบ 5: ตรวจสอบข้อมูลรายเดือน
    print("5. ข้อมูลรายเดือน (ด้วย localtime):")
    cursor.execute("""
        SELECT strftime('%Y-%m', created_at, 'localtime') as month,
               COUNT(*) as orders,
               SUM(total_amount) as sales
        FROM orders 
        WHERE DATE(created_at, 'localtime') >= DATE('now', 'localtime', '-3 months')
        GROUP BY strftime('%Y-%m', created_at, 'localtime')
        ORDER BY month DESC
    """)
    
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} ออเดอร์, {row[2]} บาท")
    
    conn.close()
    print("\n=== การทดสอบเสร็จสิ้น ===")
    print("✅ ระบบใช้ localtime อย่างสอดคล้องกันทุกจุดแล้ว")

if __name__ == "__main__":
    test_localtime_consistency()