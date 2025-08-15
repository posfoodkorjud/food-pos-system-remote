#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import DatabaseManager
from datetime import date

def check_rejected_orders():
    """ตรวจสอบออเดอร์ที่ปฏิเสธ"""
    
    db = DatabaseManager()
    
    print(f"=== ตรวจสอบออเดอร์ที่ปฏิเสธ ===")
    
    # ดึงออเดอร์ทั้งหมด
    orders = db.get_all_orders()
    rejected_orders = [o for o in orders if o.get('status') == 'rejected']
    
    print(f"จำนวนออเดอร์ที่ปฏิเสธทั้งหมด: {len(rejected_orders)}")
    
    if rejected_orders:
        print("\nออเดอร์ที่ปฏิเสธ 5 รายการล่าสุด:")
        for order in rejected_orders[-5:]:
            order_id = order.get('order_id')
            amount = order.get('total_amount', 0)
            created_at = order.get('created_at', '')[:10]
            print(f"  Order {order_id}: amount=฿{amount}, date={created_at}")
    
    # ตรวจสอบออเดอร์วันนี้
    today = date.today().strftime('%Y-%m-%d')
    today_orders = db.get_orders_by_date_range(today, today)
    today_rejected = [o for o in today_orders if o.get('status') == 'rejected']
    
    print(f"\n=== ออเดอร์วันนี้ ({today}) ===")
    print(f"ออเดอร์ทั้งหมดวันนี้: {len(today_orders)}")
    print(f"ออเดอร์ที่ปฏิเสธวันนี้: {len(today_rejected)}")
    
    if today_rejected:
        print("\nออเดอร์ที่ปฏิเสธวันนี้:")
        for order in today_rejected:
            order_id = order.get('order_id')
            amount = order.get('total_amount', 0)
            print(f"  Order {order_id}: amount=฿{amount}")
    else:
        print("ไม่มีออเดอร์ที่ปฏิเสธวันนี้")

if __name__ == '__main__':
    check_rejected_orders()