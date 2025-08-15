#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import DatabaseManager

def check_order_range():
    """ตรวจสอบ order ในช่วง 88-133"""
    try:
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # ตรวจสอบโครงสร้างตาราง orders ก่อน
        cursor.execute("PRAGMA table_info(orders)")
        columns = cursor.fetchall()
        print("คอลัมน์ในตาราง orders:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # ตรวจสอบ order ทั้งหมดในช่วง 88-133
        cursor.execute("""
            SELECT order_id, table_id, total_amount, status, completed_at
            FROM orders 
            WHERE order_id BETWEEN 88 AND 133
            ORDER BY order_id DESC
        """)
        
        orders = cursor.fetchall()
        
        print(f"\nพบ {len(orders)} orders ในช่วง 88-133:")
        print("Order ID | Table | Amount | Status | Completed")
        print("-" * 60)
        
        for order in orders:
            order_id, table_id, total_amount, status, completed_at = order
            print(f"{order_id:8} | {table_id:5} | {total_amount:6} | {status:8} | {completed_at or 'None'}")
        
        # ตรวจสอบ order items สำหรับ orders เหล่านี้
        cursor.execute("""
            SELECT oi.order_id, COUNT(*) as item_count
            FROM order_items oi
            WHERE oi.order_id BETWEEN 88 AND 133
            GROUP BY oi.order_id
            ORDER BY oi.order_id DESC
        """)
        
        order_items = cursor.fetchall()
        
        print(f"\nOrder items สำหรับ orders ในช่วง 88-133:")
        print("Order ID | Item Count")
        print("-" * 20)
        
        for order_id, item_count in order_items:
            print(f"{order_id:8} | {item_count:10}")
        
        conn.close()
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    check_order_range()