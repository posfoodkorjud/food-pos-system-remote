#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect('A_FOOD_POS/FOOD_POS/pos_database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== ตรวจสอบโครงสร้างตาราง orders ===")

# ตรวจสอบว่ามีตาราง orders หรือไม่
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
table_exists = cursor.fetchone()

if table_exists:
    print("✅ ตาราง 'orders' มีอยู่")
    
    # ดูโครงสร้างตาราง
    cursor.execute("PRAGMA table_info(orders)")
    columns = cursor.fetchall()
    
    print("\nโครงสร้างตาราง orders:")
    for col in columns:
        print(f"  {col['name']} ({col['type']}) - {'NOT NULL' if col['notnull'] else 'NULL'}")
    
    # ตรวจสอบข้อมูลตัวอย่าง
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 5")
    orders = cursor.fetchall()
    
    print("\nข้อมูลตัวอย่าง 5 รายการล่าสุด:")
    for order in orders:
        print(f"  Order ID: {order['order_id']}, Table: {order['table_id']}, Status: {order['status']}")
        print(f"  Total: {order['total_amount']}, Created: {order['created_at']}")
        print("  ---")
        
else:
    print("❌ ไม่พบตาราง 'orders'")
    
    # ดูตารางทั้งหมด
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\nตารางที่มีอยู่:")
    for table in tables:
        print(f"  - {table['name']}")

# ทดสอบฟังก์ชัน get_orders_by_date_range โดยตรง
print("\n=== ทดสอบ SQL Query ที่ใช้ใน get_orders_by_date_range ===")

start_date = '2025-08-05'
end_date = '2025-08-11'

try:
    # SQL Query เดียวกับที่ใช้ในฟังก์ชัน
    cursor.execute('''
        SELECT o.order_id, o.table_id, o.session_id, o.status, o.total_amount,
               o.created_at, o.completed_at, t.table_name
        FROM orders o
        JOIN tables t ON o.table_id = t.table_id
        WHERE DATE(o.created_at) BETWEEN ? AND ?
        ORDER BY o.created_at DESC
    ''', (start_date, end_date))
    
    orders = cursor.fetchall()
    print(f"จำนวนออเดอร์ที่พบ: {len(orders)}")
    
    total_amount = 0
    for order in orders:
        if order['status'] != 'rejected':
            total_amount += order['total_amount'] or 0
            print(f"Order {order['order_id']}: {order['total_amount']} บาท (status: {order['status']})")
    
    print(f"\nยอดขายรวม: {total_amount} บาท")
    
except Exception as e:
    print(f"เกิดข้อผิดพลาด: {e}")
    
    # ลองใช้ query ง่ายๆ
    print("\nลองใช้ query ง่ายๆ:")
    cursor.execute('''
        SELECT order_id, status, total_amount, created_at
        FROM orders
        WHERE DATE(created_at) BETWEEN ? AND ?
        ORDER BY created_at DESC
    ''', (start_date, end_date))
    
    simple_orders = cursor.fetchall()
    print(f"จำนวนออเดอร์ (query ง่าย): {len(simple_orders)}")
    
    simple_total = 0
    for order in simple_orders:
        if order['status'] != 'rejected':
            simple_total += order['total_amount'] or 0
    
    print(f"ยอดขายรวม (query ง่าย): {simple_total} บาท")

conn.close()