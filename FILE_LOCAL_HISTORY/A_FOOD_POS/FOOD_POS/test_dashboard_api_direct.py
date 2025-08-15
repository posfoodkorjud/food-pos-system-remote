#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import DatabaseManager
from datetime import datetime, date, timedelta

def test_dashboard_api_logic():
    """ทดสอบลอจิกของ API dashboard-data โดยตรง"""
    
    db = DatabaseManager()
    
    # ใช้ลอจิกเดียวกับใน API
    start_date = None
    end_date = None
    
    print(f"=== ทดสอบลอจิก Dashboard API ===")
    
    # ถ้าไม่มีการระบุวันที่ ให้ใช้วันนี้
    if not start_date or not end_date:
        today = date.today().strftime('%Y-%m-%d')
        start_date = today
        end_date = today
        
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")
    
    # ดึงข้อมูลจากฐานข้อมูล
    orders = db.get_orders_by_date_range(start_date, end_date)
    print(f"Orders from get_orders_by_date_range: {len(orders)}")
    
    # คำนวณข้อมูลสำหรับ dashboard
    period_sales = 0
    today_sales = 0
    week_sales = 0
    month_sales = 0
    total_customers = 0
    daily_sales = {}
    category_sales = {}
    top_items = []
    
    # วันนี้
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    
    # สัปดาห์นี้ (7 วันที่ผ่านมา)
    week_start = (today - timedelta(days=6)).strftime('%Y-%m-%d')
    
    # เดือนนี้
    month_start = today.replace(day=1).strftime('%Y-%m-%d')
    
    print(f"Today: {today_str}")
    print(f"Week start: {week_start}")
    print(f"Month start: {month_start}")
    
    # ดึงข้อมูลสำหรับแต่ละช่วงเวลา
    today_orders = db.get_orders_by_date_range(today_str, today_str)
    week_orders = db.get_orders_by_date_range(week_start, today_str)
    month_orders = db.get_orders_by_date_range(month_start, today_str)
    
    print(f"Today orders: {len(today_orders)}")
    print(f"Week orders: {len(week_orders)}")
    print(f"Month orders: {len(month_orders)}")
    
    # คำนวณยอดขาย (รวมทุกสถานะยกเว้น rejected)
    for order in today_orders:
        if order.get('status') != 'rejected':
            today_sales += order.get('total_amount', 0)
            print(f"Today order {order.get('order_id')}: {order.get('total_amount')} (status: {order.get('status')})")
            
    for order in week_orders:
        if order.get('status') != 'rejected':
            week_sales += order.get('total_amount', 0)
            
    for order in month_orders:
        if order.get('status') != 'rejected':
            month_sales += order.get('total_amount', 0)
    
    # ยอดขายในช่วงที่เลือก
    for order in orders:
        if order.get('status') != 'rejected':
            period_sales += order.get('total_amount', 0)
            total_customers += 1
            
            # จัดกลุ่มตามวันที่สำหรับ chart
            order_date = order.get('created_at', '')[:10]  # YYYY-MM-DD
            if order_date not in daily_sales:
                daily_sales[order_date] = {'sales': 0, 'orders': 0}
            daily_sales[order_date]['sales'] += order.get('total_amount', 0)
            daily_sales[order_date]['orders'] += 1
    
    print(f"\n=== ผลลัพธ์ ===")
    print(f"Period Sales: {period_sales}")
    print(f"Today Sales: {today_sales}")
    print(f"Week Sales: {week_sales}")
    print(f"Month Sales: {month_sales}")
    print(f"Total Customers: {total_customers}")
    print(f"Daily Sales: {daily_sales}")
    
    # สร้างข้อมูล response เหมือน API
    response_data = {
        'periodSales': period_sales,
        'todaySales': today_sales,
        'weekSales': week_sales,
        'currentWeekSales': week_sales,
        'monthSales': month_sales,
        'totalCustomers': total_customers,
        'dailySales': daily_sales,
        'categorySales': category_sales,
        'topItems': top_items,
        'monthlyTrend': []
    }
    
    print(f"\n=== Response Data ===")
    print(response_data)

if __name__ == '__main__':
    test_dashboard_api_logic()