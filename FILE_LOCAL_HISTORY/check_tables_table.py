#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

# Connect to database
conn = sqlite3.connect('A_FOOD_POS/FOOD_POS/pos_database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== ตรวจสอบตาราง tables ===")

# ตรวจสอบว่ามีตาราง tables หรือไม่
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tables'")
table_exists = cursor.fetchone()

if table_exists:
    print("✅ ตาราง 'tables' มีอยู่")
    
    # ดูโครงสร้างตาราง
    cursor.execute("PRAGMA table_info(tables)")
    columns = cursor.fetchall()
    
    print("\nโครงสร้างตาราง tables:")
    for col in columns:
        print(f"  {col['name']} ({col['type']}) - {'NOT NULL' if col['notnull'] else 'NULL'}")
    
    # ตรวจสอบข้อมูลในตาราง
    cursor.execute("SELECT * FROM tables ORDER BY table_id")
    tables = cursor.fetchall()
    
    print(f"\nจำนวนโต๊ะทั้งหมด: {len(tables)}")
    
    if tables:
        print("\nข้อมูลโต๊ะ:")
        for table in tables:
            table_name = table['table_name'] if 'table_name' in table.keys() else (table['name'] if 'name' in table.keys() else 'N/A')
            print(f"  Table ID: {table['table_id']}, Name: {table_name}")
    else:
        print("❌ ไม่มีข้อมูลในตาราง tables")
        
else:
    print("❌ ไม่พบตาราง 'tables'")

# ทดสอบ JOIN ระหว่าง orders และ tables
print("\n=== ทดสอบ JOIN ระหว่าง orders และ tables ===")

start_date = '2025-08-05'
end_date = '2025-08-11'

try:
    # ทดสอบ query โดยไม่ JOIN กับ tables
    cursor.execute('''
        SELECT o.order_id, o.table_id, o.session_id, o.status, o.total_amount,
               o.created_at, o.completed_at
        FROM orders o
        WHERE DATE(o.created_at) BETWEEN ? AND ?
        ORDER BY o.created_at DESC
    ''', (start_date, end_date))
    
    orders_no_join = cursor.fetchall()
    print(f"จำนวนออเดอร์ (ไม่ JOIN): {len(orders_no_join)}")
    
    total_no_join = 0
    for order in orders_no_join:
        if order['status'] != 'rejected':
            total_no_join += order['total_amount'] or 0
    
    print(f"ยอดขายรวม (ไม่ JOIN): {total_no_join} บาท")
    
    # ทดสอบ query แบบ LEFT JOIN
    cursor.execute('''
        SELECT o.order_id, o.table_id, o.session_id, o.status, o.total_amount,
               o.created_at, o.completed_at, t.table_name
        FROM orders o
        LEFT JOIN tables t ON o.table_id = t.table_id
        WHERE DATE(o.created_at) BETWEEN ? AND ?
        ORDER BY o.created_at DESC
    ''', (start_date, end_date))
    
    orders_left_join = cursor.fetchall()
    print(f"จำนวนออเดอร์ (LEFT JOIN): {len(orders_left_join)}")
    
    total_left_join = 0
    for order in orders_left_join:
        if order['status'] != 'rejected':
            total_left_join += order['total_amount'] or 0
    
    print(f"ยอดขายรวม (LEFT JOIN): {total_left_join} บาท")
    
    # ทดสอบ query แบบ INNER JOIN (เหมือนในโค้ด)
    cursor.execute('''
        SELECT o.order_id, o.table_id, o.session_id, o.status, o.total_amount,
               o.created_at, o.completed_at, t.table_name
        FROM orders o
        JOIN tables t ON o.table_id = t.table_id
        WHERE DATE(o.created_at) BETWEEN ? AND ?
        ORDER BY o.created_at DESC
    ''', (start_date, end_date))
    
    orders_inner_join = cursor.fetchall()
    print(f"จำนวนออเดอร์ (INNER JOIN): {len(orders_inner_join)}")
    
    total_inner_join = 0
    for order in orders_inner_join:
        if order['status'] != 'rejected':
            total_inner_join += order['total_amount'] or 0
    
    print(f"ยอดขายรวม (INNER JOIN): {total_inner_join} บาท")
    
    # ตรวจสอบ table_id ที่ไม่มีใน tables
    cursor.execute('''
        SELECT DISTINCT o.table_id
        FROM orders o
        LEFT JOIN tables t ON o.table_id = t.table_id
        WHERE t.table_id IS NULL AND DATE(o.created_at) BETWEEN ? AND ?
    ''', (start_date, end_date))
    
    missing_tables = cursor.fetchall()
    if missing_tables:
        print(f"\n❌ table_id ที่ไม่มีในตาราง tables: {[row['table_id'] for row in missing_tables]}")
    else:
        print("\n✅ ทุก table_id มีอยู่ในตาราง tables")
        
except Exception as e:
    print(f"เกิดข้อผิดพลาด: {e}")

conn.close()