#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('backend')
from database import DatabaseManager
from datetime import date, timedelta

def test_sales_data():
    """ทดสอบข้อมูลยอดขายเพื่อหาสาเหตุที่แสดง 0"""
    
    db = DatabaseManager()
    
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    
    print(f"=== ทดสอบข้อมูลยอดขาย วันที่ {today_str} ===")
    
    # ทดสอบดึงข้อมูลออเดอร์วันนี้
    print("\n1. ทดสอบดึงออเดอร์วันนี้:")
    today_orders = db.get_orders_by_date_range(today_str, today_str)
    print(f"   จำนวนออเดอร์วันนี้: {len(today_orders)}")
    
    if today_orders:
        print("   ออเดอร์วันนี้:")
        for order in today_orders[:3]:  # แสดง 3 รายการแรก
            print(f"     - Order ID: {order['order_id']}, Status: {order['status']}, Total: {order['total_amount']}")
    
    # ทดสอบดึงข้อมูลออเดอร์ทั้งหมด
    print("\n2. ทดสอบดึงออเดอร์ทั้งหมด:")
    all_orders = db.get_orders_by_date_range('2020-01-01', today_str)
    print(f"   จำนวนออเดอร์ทั้งหมด: {len(all_orders)}")
    
    # นับออเดอร์ตามสถานะ
    completed_orders = [o for o in all_orders if o.get('status') == 'completed']
    print(f"   ออเดอร์ที่เสร็จสิ้น: {len(completed_orders)}")
    
    if completed_orders:
        print("   ออเดอร์ที่เสร็จสิ้น (3 รายการแรก):")
        for order in completed_orders[:3]:
            print(f"     - Order ID: {order['order_id']}, Total: {order['total_amount']}, Date: {order['created_at']}")
    
    # คำนวณยอดรวม
    total_sales = sum(order.get('total_amount', 0) for order in completed_orders)
    print(f"\n3. ยอดขายรวม: {total_sales} บาท")
    
    # ตรวจสอบข้อมูลออเดอร์ที่มี total_amount เป็น 0 หรือ None
    zero_total_orders = [o for o in all_orders if not o.get('total_amount')]
    print(f"\n4. ออเดอร์ที่มี total_amount เป็น 0 หรือ None: {len(zero_total_orders)}")
    
    if zero_total_orders:
        print("   ตัวอย่างออเดอร์ที่มี total_amount เป็น 0:")
        for order in zero_total_orders[:3]:
            print(f"     - Order ID: {order['order_id']}, Status: {order['status']}, Total: {order['total_amount']}")

if __name__ == '__main__':
    test_sales_data()