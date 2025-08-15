#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

def check_database_dates():
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    # ตรวจสอบวันที่ทั้งหมดในฐานข้อมูล
    cursor.execute("SELECT DISTINCT DATE(created_at) FROM orders ORDER BY DATE(created_at) DESC LIMIT 10")
    dates = cursor.fetchall()
    print("วันที่ล่าสุดในฐานข้อมูล:")
    for date in dates:
        print(f"  {date[0]}")
    
    # ตรวจสอบข้อมูลวันที่ 2025-08-12
    cursor.execute("SELECT COUNT(*), SUM(total_amount) FROM orders WHERE DATE(created_at) = '2025-08-12'")
    result = cursor.fetchone()
    print(f"\nข้อมูลวันที่ 2025-08-12:")
    print(f"  จำนวนออเดอร์: {result[0]}")
    print(f"  ยอดรวม: {result[1]} บาท")
    
    # ตรวจสอบข้อมูลวันที่ 2025-08-12 ตามสถานะ
    cursor.execute("""
        SELECT status, COUNT(*), SUM(total_amount) 
        FROM orders 
        WHERE DATE(created_at) = '2025-08-12' 
        GROUP BY status
    """)
    status_data = cursor.fetchall()
    print(f"\nข้อมูลตามสถานะวันที่ 2025-08-12:")
    for status, count, total in status_data:
        print(f"  {status}: {count} ออเดอร์, {total} บาท")
    
    conn.close()

if __name__ == "__main__":
    check_database_dates()