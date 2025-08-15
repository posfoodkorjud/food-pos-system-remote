#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(__file__))

from backend.database import DatabaseManager
from datetime import date

def debug_calculation():
    """Debug การคำนวณยอดรวม"""
    
    db = DatabaseManager()
    today = date.today().strftime('%Y-%m-%d')
    
    print(f"=== Debug การคำนวณยอดรวม ===\n")
    print(f"วันที่: {today}")
    
    try:
        orders = db.get_orders_by_date_range(today, today)
        print(f"จำนวนออเดอร์: {len(orders)}\n")
        
        for order in orders:
            order_id = order['order_id']
            order_total = order['total_amount']
            items = order.get('items', [])
            
            print(f"Order {order_id}:")
            print(f"  Total amount จากฟังก์ชัน: {order_total} บาท")
            
            # คำนวณใหม่เพื่อ debug
            manual_total = 0
            rejected_total = 0
            
            for item in items:
                status = item.get('status', 'pending')
                price = item.get('total_price', 0)
                name = item.get('name', 'Unknown')
                
                print(f"    - {name}: {price} บาท (status: {status})")
                
                if status == 'rejected':
                    rejected_total += price
                else:
                    manual_total += price
            
            print(f"  Manual calculation (non-rejected): {manual_total} บาท")
            print(f"  Rejected items total: {rejected_total} บาท")
            print(f"  All items total: {manual_total + rejected_total} บาท")
            print(f"  ✅ Correct? {order_total == manual_total}\n")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_calculation()