#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import DatabaseManager

def check_latest_orders():
    """ตรวจสอบ order ล่าสุดทั้งหมดในฐานข้อมูล"""
    try:
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # ตรวจสอบ order ล่าสุด 20 รายการ
        print("=== ตรวจสอบ Order ล่าสุด 20 รายการ ===")
        cursor.execute("""
            SELECT order_id, table_id, total_amount, status, 
                   datetime(created_at, 'localtime') as created_at,
                   datetime(completed_at, 'localtime') as completed_at
            FROM orders 
            ORDER BY order_id DESC 
            LIMIT 20
        """)
        
        latest_orders = cursor.fetchall()
        
        if latest_orders:
            print(f"พบ {len(latest_orders)} orders ล่าสุด:")
            for order in latest_orders:
                order_id, table_id, total_amount, status, created_at, completed_at = order
                print(f"Order {order_id}: โต๊ะ {table_id}, ยอดรวม {total_amount:.2f} บาท, สถานะ: {status}")
                print(f"  สร้างเมื่อ: {created_at}")
                if completed_at:
                    print(f"  เสร็จเมื่อ: {completed_at}")
                print()
        else:
            print("ไม่พบ order ใดๆ ในฐานข้อมูล")
        
        # ตรวจสอบ order สูงสุดและต่ำสุด
        print("=== ช่วง Order ID ในฐานข้อมูล ===")
        cursor.execute("SELECT MIN(order_id), MAX(order_id), COUNT(*) FROM orders")
        min_id, max_id, total_count = cursor.fetchone()
        
        print(f"Order ID ต่ำสุด: {min_id}")
        print(f"Order ID สูงสุด: {max_id}")
        print(f"จำนวน orders ทั้งหมด: {total_count}")
        
        # ตรวจสอบ order ที่มากกว่า 133
        print("\n=== Order ที่มากกว่า 133 ===")
        cursor.execute("""
            SELECT order_id, table_id, total_amount, status,
                   datetime(created_at, 'localtime') as created_at,
                   datetime(completed_at, 'localtime') as completed_at
            FROM orders 
            WHERE order_id > 133
            ORDER BY order_id DESC
        """)
        
        orders_above_133 = cursor.fetchall()
        
        if orders_above_133:
            print(f"พบ {len(orders_above_133)} orders ที่มากกว่า 133:")
            for order in orders_above_133:
                order_id, table_id, total_amount, status, created_at, completed_at = order
                print(f"Order {order_id}: โต๊ะ {table_id}, ยอดรวม {total_amount:.2f} บาท, สถานะ: {status}")
                print(f"  สร้างเมื่อ: {created_at}")
                if completed_at:
                    print(f"  เสร็จเมื่อ: {completed_at}")
                print()
        else:
            print("ไม่พบ order ที่มากกว่า 133")
        
        conn.close()
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    check_latest_orders()