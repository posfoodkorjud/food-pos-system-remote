#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import DatabaseManager
from datetime import datetime, date

def test_get_orders_function():
    """ทดสอบฟังก์ชัน get_orders_by_date_range โดยตรง"""
    
    db = DatabaseManager()
    today = date.today().strftime('%Y-%m-%d')
    
    print(f"=== ทดสอบฟังก์ชัน get_orders_by_date_range สำหรับวันที่ {today} ===")
    
    try:
        # เรียกใช้ฟังก์ชันโดยตรง
        orders = db.get_orders_by_date_range(today, today)
        
        print(f"✅ ฟังก์ชันทำงานสำเร็จ")
        print(f"จำนวนออเดอร์ที่ได้: {len(orders)}")
        
        if orders:
            print("\nรายละเอียดออเดอร์:")
            total_amount = 0
            for order in orders:
                print(f"Order ID: {order.get('order_id')}")
                print(f"Status: {order.get('status')}")
                print(f"Total Amount: {order.get('total_amount')}")
                print(f"Created At: {order.get('created_at')}")
                print(f"Items count: {len(order.get('items', []))}")
                
                if order.get('status') != 'rejected':
                    total_amount += order.get('total_amount', 0)
                
                print("-" * 30)
                
            print(f"\nยอดขายรวม (ไม่รวม rejected): {total_amount} บาท")
        else:
            print("ไม่พบออเดอร์สำหรับวันนี้")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_get_orders_function()