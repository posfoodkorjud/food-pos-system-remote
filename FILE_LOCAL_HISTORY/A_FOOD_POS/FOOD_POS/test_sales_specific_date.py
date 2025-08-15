#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('backend')
from database import DatabaseManager
from datetime import date, timedelta

def test_sales_specific_date():
    """ทดสอบข้อมูลยอดขายในวันที่มีข้อมูลจริง"""
    
    db = DatabaseManager()
    
    # ทดสอบกับวันที่ 2025-08-08 ที่มีข้อมูล
    test_date = '2025-08-08'
    
    print(f"=== ทดสอบข้อมูลยอดขาย วันที่ {test_date} ===")
    
    # ทดสอบดึงข้อมูลออเดอร์วันที่ 2025-08-08
    orders = db.get_orders_by_date_range(test_date, test_date)
    print(f"จำนวนออเดอร์วันที่ {test_date}: {len(orders)}")
    
    if orders:
        print("ออเดอร์ทั้งหมด:")
        for order in orders:
            print(f"  - Order ID: {order['order_id']}, Status: {order['status']}, Total: {order['total_amount']}, Created: {order['created_at']}")
    
    # นับออเดอร์ที่เสร็จสิ้น
    completed_orders = [o for o in orders if o.get('status') == 'completed']
    print(f"\nออเดอร์ที่เสร็จสิ้น: {len(completed_orders)}")
    
    # คำนวณยอดรวม
    total_sales = sum(order.get('total_amount', 0) for order in completed_orders)
    print(f"ยอดขายรวมวันที่ {test_date}: {total_sales} บาท")
    
    # ทดสอบช่วงวันที่ที่กว้างขึ้น
    print(f"\n=== ทดสอบช่วงวันที่ 2025-08-01 ถึง 2025-08-10 ===")
    range_orders = db.get_orders_by_date_range('2025-08-01', '2025-08-10')
    print(f"จำนวนออเดอร์ในช่วงนี้: {len(range_orders)}")
    
    range_completed = [o for o in range_orders if o.get('status') == 'completed']
    range_total = sum(order.get('total_amount', 0) for order in range_completed)
    print(f"ยอดขายรวมในช่วงนี้: {range_total} บาท")
    
    # แสดงวันที่ที่มีออเดอร์
    dates_with_orders = set()
    for order in range_orders:
        if order.get('created_at'):
            order_date = order['created_at'][:10]  # เอาแค่ส่วนวันที่
            dates_with_orders.add(order_date)
    
    print(f"\nวันที่ที่มีออเดอร์: {sorted(dates_with_orders)}")

if __name__ == '__main__':
    test_sales_specific_date()