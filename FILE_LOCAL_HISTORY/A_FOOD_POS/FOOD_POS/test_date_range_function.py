#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import DatabaseManager
from datetime import datetime

def test_date_range_function():
    """ทดสอบฟังก์ชัน get_orders_by_date_range โดยตรง"""
    
    db = DatabaseManager()
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"=== ทดสอบฟังก์ชัน get_orders_by_date_range สำหรับวันที่ {today} ===")
    
    # เรียกใช้ฟังก์ชันโดยตรง
    orders = db.get_orders_by_date_range(today, today)
    
    print(f"จำนวนออเดอร์ที่ได้: {len(orders)}")
    
    if orders:
        print("\nรายละเอียดออเดอร์:")
        for order in orders:
            print(f"Order ID: {order.get('order_id')}")
            print(f"Status: {order.get('status')}")
            print(f"Total Amount: {order.get('total_amount')}")
            print(f"Created At: {order.get('created_at')}")
            print(f"Table ID: {order.get('table_id')}")
            print("-" * 30)
            
        # คำนวณยอดขายรวม (ยกเว้น rejected)
        total_sales = 0
        completed_orders = 0
        for order in orders:
            if order.get('status') != 'rejected':
                total_sales += order.get('total_amount', 0)
                completed_orders += 1
                
        print(f"\nสรุป:")
        print(f"ออเดอร์ที่ไม่ใช่ rejected: {completed_orders}")
        print(f"ยอดขายรวม: {total_sales} บาท")
    else:
        print("ไม่พบออเดอร์สำหรับวันนี้")
        
    # ทดสอบด้วยช่วงวันที่ที่กว้างขึ้น
    print(f"\n=== ทดสอบช่วงวันที่ 2025-08-01 ถึง {today} ===")
    range_orders = db.get_orders_by_date_range('2025-08-01', today)
    print(f"จำนวนออเดอร์ในช่วงนี้: {len(range_orders)}")
    
    if range_orders:
        range_total = 0
        for order in range_orders:
            if order.get('status') != 'rejected':
                range_total += order.get('total_amount', 0)
        print(f"ยอดขายรวมในช่วงนี้: {range_total} บาท")
        
        # แสดงวันที่ที่มีออเดอร์
        dates_with_orders = set()
        for order in range_orders:
            if order.get('created_at'):
                order_date = order['created_at'][:10]  # เอาแค่ส่วนวันที่
                dates_with_orders.add(order_date)
        
        print(f"วันที่ที่มีออเดอร์: {sorted(dates_with_orders)}")

if __name__ == '__main__':
    test_date_range_function()