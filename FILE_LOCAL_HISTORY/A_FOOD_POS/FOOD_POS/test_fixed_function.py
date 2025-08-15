#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(__file__))

from backend.database import DatabaseManager
from datetime import date

def test_fixed_function():
    """ทดสอบฟังก์ชัน get_orders_by_date_range ที่แก้ไขแล้ว"""
    
    db = DatabaseManager()
    today = date.today().strftime('%Y-%m-%d')
    
    print(f"=== ทดสอบฟังก์ชัน get_orders_by_date_range ที่แก้ไขแล้ว ===\n")
    print(f"วันที่: {today}")
    
    try:
        orders = db.get_orders_by_date_range(today, today)
        print(f"จำนวนออเดอร์: {len(orders)}\n")
        
        total_sales = 0
        for order in orders:
            order_id = order['order_id']
            order_total = order['total_amount']
            items = order.get('items', [])
            
            print(f"Order {order_id}: {order_total} บาท")
            print(f"  รายการอาหาร ({len(items)} รายการ):")
            
            for item in items:
                status = item.get('status', 'pending')
                price = item.get('total_price', 0)
                name = item.get('name', 'Unknown')
                print(f"    - {name}: {price} บาท (status: {status})")
            
            total_sales += order_total
            print()
        
        print(f"=== สรุป ===\n")
        print(f"ยอดขายรวมวันนี้: {total_sales} บาท")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_fixed_function()