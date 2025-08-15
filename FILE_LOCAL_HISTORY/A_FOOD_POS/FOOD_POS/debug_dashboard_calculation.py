#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import DatabaseManager
from datetime import datetime, date, timedelta

def debug_dashboard_calculation():
    """Debug การคำนวณข้อมูล dashboard"""
    
    db = DatabaseManager()
    
    # วันที่ต่างๆ
    today_date = date.today()
    today_str = today_date.strftime('%Y-%m-%d')
    week_start = (today_date - timedelta(days=6)).strftime('%Y-%m-%d')
    month_start = today_date.replace(day=1).strftime('%Y-%m-%d')
    
    print(f"=== Debug Dashboard Calculation ===")
    print(f"Today: {today_str}")
    print(f"Week start: {week_start}")
    print(f"Month start: {month_start}")
    
    # ทดสอบการดึงข้อมูลแต่ละช่วงเวลา
    print(f"\n=== ทดสอบการดึงข้อมูลออเดอร์ ===")
    
    try:
        # วันนี้
        today_orders = db.get_orders_by_date_range(today_str, today_str)
        print(f"Today orders: {len(today_orders)}")
        
        # สัปดาห์นี้
        week_orders = db.get_orders_by_date_range(week_start, today_str)
        print(f"Week orders: {len(week_orders)}")
        
        # เดือนนี้
        month_orders = db.get_orders_by_date_range(month_start, today_str)
        print(f"Month orders: {len(month_orders)}")
        
        # คำนวณยอดขาย
        print(f"\n=== คำนวณยอดขาย ===")
        
        today_sales = 0
        week_sales = 0
        month_sales = 0
        total_customers = 0
        
        # วันนี้
        for order in today_orders:
            if order.get('status') != 'rejected':
                today_sales += order.get('total_amount', 0)
                print(f"Today order {order.get('order_id')}: {order.get('total_amount')} (status: {order.get('status')})")
        
        # สัปดาห์
        for order in week_orders:
            if order.get('status') != 'rejected':
                week_sales += order.get('total_amount', 0)
        
        # เดือน
        for order in month_orders:
            if order.get('status') != 'rejected':
                month_sales += order.get('total_amount', 0)
                total_customers += 1
        
        print(f"\n=== ผลลัพธ์ ===")
        print(f"Today Sales: {today_sales}")
        print(f"Week Sales: {week_sales}")
        print(f"Month Sales: {month_sales}")
        print(f"Total Customers: {total_customers}")
        
        # ตรวจสอบข้อมูลออเดอร์วันนี้อย่างละเอียด
        if today_orders:
            print(f"\n=== รายละเอียดออเดอร์วันนี้ ===")
            for order in today_orders:
                print(f"Order ID: {order.get('order_id')}")
                print(f"Status: {order.get('status')}")
                print(f"Total Amount: {order.get('total_amount')}")
                print(f"Created At: {order.get('created_at')}")
                print(f"Items: {len(order.get('items', []))}")
                
                # แสดงรายการ items
                for item in order.get('items', []):
                    print(f"  - {item.get('name')}: {item.get('quantity')} x {item.get('unit_price')} = {item.get('total_price')}")
                print("-" * 50)
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_dashboard_calculation()