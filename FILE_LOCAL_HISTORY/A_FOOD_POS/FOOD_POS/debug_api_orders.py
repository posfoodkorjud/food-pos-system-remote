#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import DatabaseManager
from datetime import datetime, date, timedelta
import json

def debug_api_orders():
    """Debug ข้อมูล orders ที่ API ได้รับ"""
    
    db = DatabaseManager()
    
    # Import datetime modules
    from datetime import date, timedelta
    
    # ถ้าไม่มีการระบุวันที่ ให้ใช้วันนี้
    start_date = None
    end_date = None
    
    if not start_date or not end_date:
        today_date = date.today()
        today_str = today_date.strftime('%Y-%m-%d')
        start_date = today_str
        end_date = today_str
    
    print(f"=== Debug API Orders ===")
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")
    
    # ดึงข้อมูลจากฐานข้อมูล
    orders = db.get_orders_by_date_range(start_date, end_date)
    print(f"Orders from get_orders_by_date_range: {len(orders)}")
    
    # แสดงข้อมูล orders ทั้งหมด
    for i, order in enumerate(orders):
        print(f"\nOrder {i+1}:")
        print(f"  ID: {order.get('order_id')}")
        print(f"  Status: {order.get('status')}")
        print(f"  Total Amount: {order.get('total_amount')}")
        print(f"  Created At: {order.get('created_at')}")
        print(f"  Full Order Data: {json.dumps(order, indent=2, ensure_ascii=False)}")
    
    # คำนวณข้อมูลสำหรับ dashboard
    period_sales = 0
    today_sales = 0
    week_sales = 0
    month_sales = 0
    total_customers = 0
    daily_sales = {}
    
    # วันนี้
    today_date = date.today()
    today_str = today_date.strftime('%Y-%m-%d')
    
    # สัปดาห์นี้ (7 วันที่ผ่านมา)
    week_start = (today_date - timedelta(days=6)).strftime('%Y-%m-%d')
    
    # เดือนนี้
    month_start = today_date.replace(day=1).strftime('%Y-%m-%d')
    
    print(f"\n=== Date Ranges ===")
    print(f"Today: {today_str}")
    print(f"Week start: {week_start}")
    print(f"Month start: {month_start}")
    
    # ดึงข้อมูลสำหรับแต่ละช่วงเวลา
    today_orders = db.get_orders_by_date_range(today_str, today_str)
    week_orders = db.get_orders_by_date_range(week_start, today_str)
    month_orders = db.get_orders_by_date_range(month_start, today_str)
    
    print(f"\n=== Order Counts ===")
    print(f"Today orders: {len(today_orders)}")
    print(f"Week orders: {len(week_orders)}")
    print(f"Month orders: {len(month_orders)}")
    
    # คำนวณยอดขาย (รวมทุกสถานะยกเว้น rejected)
    print(f"\n=== Today Orders Detail ===")
    for order in today_orders:
        print(f"Order {order.get('order_id')}: status={order.get('status')}, amount={order.get('total_amount')}")
        if order.get('status') != 'rejected':
            today_sales += order.get('total_amount', 0)
            print(f"  -> Added to today_sales: {order.get('total_amount', 0)}")
        else:
            print(f"  -> Rejected, not added")
            
    print(f"\n=== Week Orders Detail ===")
    for order in week_orders:
        if order.get('status') != 'rejected':
            week_sales += order.get('total_amount', 0)
            
    print(f"\n=== Month Orders Detail ===")
    for order in month_orders:
        if order.get('status') != 'rejected':
            month_sales += order.get('total_amount', 0)
    
    # ยอดขายในช่วงที่เลือก
    print(f"\n=== Period Orders Detail ===")
    for order in orders:
        print(f"Order {order.get('order_id')}: status={order.get('status')}, amount={order.get('total_amount')}")
        if order.get('status') != 'rejected':
            period_sales += order.get('total_amount', 0)
            total_customers += 1
            print(f"  -> Added to period_sales: {order.get('total_amount', 0)}")
            
            # จัดกลุ่มตามวันที่สำหรับ chart
            order_date = order.get('created_at', '')[:10]  # YYYY-MM-DD
            if order_date not in daily_sales:
                daily_sales[order_date] = {'sales': 0, 'orders': 0}
            daily_sales[order_date]['sales'] += order.get('total_amount', 0)
            daily_sales[order_date]['orders'] += 1
        else:
            print(f"  -> Rejected, not added")
    
    print(f"\n=== Final Results ===")
    print(f"Period Sales: {period_sales}")
    print(f"Today Sales: {today_sales}")
    print(f"Week Sales: {week_sales}")
    print(f"Month Sales: {month_sales}")
    print(f"Total Customers: {total_customers}")
    print(f"Daily Sales: {daily_sales}")

if __name__ == '__main__':
    debug_api_orders()