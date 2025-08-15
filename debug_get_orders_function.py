#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'A_FOOD_POS', 'FOOD_POS', 'backend'))

from database import DatabaseManager
from datetime import datetime, timedelta

def debug_get_orders_function():
    """Debug ฟังก์ชัน get_orders_by_date_range โดยละเอียด"""
    
    # ใช้ path เดียวกับที่ app.py ใช้
    db = DatabaseManager("A_FOOD_POS/FOOD_POS/pos_database.db")
    
    start_date = '2025-08-05'
    end_date = '2025-08-11'
    
    print(f"=== Debug get_orders_by_date_range ===")
    print(f"ช่วงวันที่: {start_date} ถึง {end_date}")
    
    try:
        # เรียกใช้ฟังก์ชันโดยตรง
        print("\n=== เรียกใช้ฟังก์ชัน get_orders_by_date_range ===")
        orders = db.get_orders_by_date_range(start_date, end_date)
        
        print(f"ประเภทของ orders: {type(orders)}")
        print(f"จำนวนออเดอร์ที่ได้: {len(orders)}")
        
        if orders:
            print("\nรายละเอียดออเดอร์:")
            total_amount = 0
            for i, order in enumerate(orders):
                print(f"\nOrder {i+1}:")
                print(f"  Type: {type(order)}")
                print(f"  Keys: {list(order.keys()) if hasattr(order, 'keys') else 'No keys method'}")
                
                if isinstance(order, dict):
                    print(f"  Order ID: {order.get('order_id')}")
                    print(f"  Status: {order.get('status')}")
                    print(f"  Total Amount: {order.get('total_amount')}")
                    print(f"  Created At: {order.get('created_at')}")
                    print(f"  Items: {len(order.get('items', []))}")
                    
                    if order.get('status') != 'rejected':
                        amount = order.get('total_amount', 0) or 0
                        total_amount += amount
                        print(f"  ✅ รวมในการคำนวณ: {amount} บาท")
                    else:
                        print(f"  ❌ ไม่รวมในการคำนวณ (rejected)")
                else:
                    print(f"  ⚠️ Order ไม่ใช่ dict: {order}")
                    
                if i >= 4:  # แสดงแค่ 5 รายการแรก
                    print(f"  ... และอีก {len(orders) - 5} รายการ")
                    break
            
            print(f"\n=== สรุป ===")
            print(f"ยอดขายรวม: {total_amount} บาท")
            
        else:
            print("❌ ไม่พบออเดอร์")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
        
    # ทดสอบการเชื่อมต่อฐานข้อมูล
    print("\n=== ทดสอบการเชื่อมต่อฐานข้อมูล ===")
    try:
        conn = db.get_connection()
        print(f"✅ เชื่อมต่อฐานข้อมูลสำเร็จ: {conn}")
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM orders WHERE DATE(created_at) BETWEEN ? AND ?", (start_date, end_date))
        count_result = cursor.fetchone()
        print(f"จำนวนออเดอร์ในฐานข้อมูล: {count_result['count'] if count_result else 'N/A'}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล: {e}")
        
    # ทดสอบ database path
    print("\n=== ทดสอบ Database Path ===")
    print(f"Database Manager DB Path: {getattr(db, 'db_path', 'ไม่พบ attribute db_path')}")
    
    # ตรวจสอบไฟล์ฐานข้อมูล
    possible_paths = [
        'A_FOOD_POS/FOOD_POS/pos_database.db',
        'A_FOOD_POS/FOOD_POS/data/food_pos.db',
        '../pos_database.db',
        'pos_database.db'
    ]
    
    for path in possible_paths:
        full_path = os.path.abspath(path)
        exists = os.path.exists(full_path)
        print(f"  {path} -> {full_path} ({'✅ มีอยู่' if exists else '❌ ไม่มี'})")

if __name__ == '__main__':
    debug_get_orders_function()