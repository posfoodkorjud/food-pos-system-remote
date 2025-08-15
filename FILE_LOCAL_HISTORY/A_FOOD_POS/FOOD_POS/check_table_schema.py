#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_order_items_schema():
    """ตรวจสอบโครงสร้างตาราง order_items"""
    
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    print("=== โครงสร้างตาราง order_items ===")
    cursor.execute("PRAGMA table_info(order_items)")
    columns = cursor.fetchall()
    
    for column in columns:
        print(f"Column: {column[1]}, Type: {column[2]}, NotNull: {column[3]}, Default: {column[4]}, PK: {column[5]}")
    
    # ตรวจสอบว่ามีคอลัมน์ customer_request หรือไม่
    column_names = [col[1] for col in columns]
    if 'customer_request' in column_names:
        print("\n✅ คอลัมน์ customer_request มีอยู่ในตาราง")
    else:
        print("\n❌ คอลัมน์ customer_request ไม่มีในตาราง")
        print("คอลัมน์ที่มีอยู่:", column_names)
    
    # ตรวจสอบข้อมูลตัวอย่าง
    print("\n=== ข้อมูลตัวอย่าง 5 รายการล่าสุด ===")
    cursor.execute("SELECT * FROM order_items ORDER BY order_item_id DESC LIMIT 5")
    rows = cursor.fetchall()
    
    for row in rows:
        print(row)
    
    conn.close()

if __name__ == '__main__':
    check_order_items_schema()