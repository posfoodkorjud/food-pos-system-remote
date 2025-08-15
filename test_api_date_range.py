#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('A_FOOD_POS/FOOD_POS/backend')

from database import DatabaseManager
from datetime import datetime, timedelta
import requests
import json

def test_api_date_ranges():
    print("=== ทดสอบช่วงวันที่ที่ API ใช้คำนวณ ===")
    
    # ทดสอบ API
    try:
        response = requests.get('http://localhost:5000/api/dashboard-data')
        if response.status_code == 200:
            data = response.json()['data']
            print(f"API Results:")
            print(f"  Today Sales: {data['todaySales']}")
            print(f"  Week Sales: {data['weekSales']}")
            print(f"  Period Sales: {data['periodSales']}")
            print(f"  Month Sales: {data['monthSales']}")
            print(f"  Current Week Sales: {data['currentWeekSales']}")
            print(f"  Total Customers: {data['totalCustomers']}")
            
            print(f"\nDaily Sales:")
            for date, sales_data in data['dailySales'].items():
                print(f"  {date}: {sales_data['sales']} บาท ({sales_data['orders']} orders)")
        else:
            print(f"API Error: {response.status_code}")
    except Exception as e:
        print(f"API Error: {e}")
    
    print("\n=== ทดสอบฐานข้อมูลโดยตรง ===")
    
    # ทดสอบฐานข้อมูลโดยตรง
    db = DatabaseManager("A_FOOD_POS/FOOD_POS/pos_database.db")
    
    # คำนวณวันที่ต่างๆ
    today = datetime.now().date()
    week_start = today - timedelta(days=6)  # 7 วันที่แล้ว (รวมวันนี้)
    month_start = today.replace(day=1)
    
    print(f"วันนี้: {today}")
    print(f"เริ่มต้นสัปดาห์ (7 วัน): {week_start}")
    print(f"เริ่มต้นเดือน: {month_start}")
    
    # ทดสอบ get_orders_by_date_range สำหรับช่วงต่างๆ
    print("\n=== ทดสอบ get_orders_by_date_range ===")
    
    # วันนี้
    today_orders = db.get_orders_by_date_range(today, today)
    today_sales = sum(order['total_amount'] for order in today_orders if order['status'] != 'rejected')
    print(f"วันนี้ ({today}): {len(today_orders)} orders, {today_sales} บาท")
    
    # สัปดาห์นี้ (7 วัน)
    week_orders = db.get_orders_by_date_range(week_start, today)
    week_sales = sum(order['total_amount'] for order in week_orders if order['status'] != 'rejected')
    print(f"สัปดาห์นี้ ({week_start} ถึง {today}): {len(week_orders)} orders, {week_sales} บาท")
    
    # เดือนนี้
    month_orders = db.get_orders_by_date_range(month_start, today)
    month_sales = sum(order['total_amount'] for order in month_orders if order['status'] != 'rejected')
    print(f"เดือนนี้ ({month_start} ถึง {today}): {len(month_orders)} orders, {month_sales} บาท")
    
    # ทดสอบช่วงที่เราคาดหวัง (2025-08-05 ถึง 2025-08-11)
    expected_start = datetime(2025, 8, 5).date()
    expected_end = datetime(2025, 8, 11).date()
    expected_orders = db.get_orders_by_date_range(expected_start, expected_end)
    expected_sales = sum(order['total_amount'] for order in expected_orders if order['status'] != 'rejected')
    print(f"ช่วงที่คาดหวัง ({expected_start} ถึง {expected_end}): {len(expected_orders)} orders, {expected_sales} บาท")
    
    # แสดงรายละเอียดออเดอร์ในแต่ละวัน
    print("\n=== รายละเอียดออเดอร์ในแต่ละวัน ===")
    all_orders = db.get_orders_by_date_range(datetime(2025, 8, 1).date(), today)
    
    daily_summary = {}
    for order in all_orders:
        if order['status'] != 'rejected':
            order_date = order['created_at'][:10]  # YYYY-MM-DD
            if order_date not in daily_summary:
                daily_summary[order_date] = {'orders': 0, 'sales': 0}
            daily_summary[order_date]['orders'] += 1
            daily_summary[order_date]['sales'] += order['total_amount']
    
    for date in sorted(daily_summary.keys()):
        data = daily_summary[date]
        print(f"  {date}: {data['orders']} orders, {data['sales']} บาท")

if __name__ == "__main__":
    test_api_date_ranges()