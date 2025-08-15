#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import requests
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'A_FOOD_POS', 'FOOD_POS', 'backend'))

from database import DatabaseManager

def test_api_vs_direct():
    """เปรียบเทียบผลลัพธ์ระหว่าง API และการเรียกใช้ฟังก์ชันโดยตรง"""
    
    db = DatabaseManager()
    today = datetime.now()
    
    # คำนวณช่วงวันที่ 7 วัน
    start_date = (today - timedelta(days=6)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    print(f"=== ทดสอบเปรียบเทียบ API vs Direct Function ===")
    print(f"วันที่: {start_date} ถึง {end_date}")
    print(f"วันนี้: {today.strftime('%Y-%m-%d')}")
    
    # 1. ทดสอบการเรียกใช้ฟังก์ชันโดยตรง
    print("\n=== การเรียกใช้ฟังก์ชันโดยตรง ===")
    try:
        # ดึงข้อมูลโดยตรงจากฟังก์ชัน
        orders_direct = db.get_orders_by_date_range(start_date, end_date)
        print(f"จำนวนออเดอร์ที่ได้: {len(orders_direct)}")
        
        # คำนวณยอดขาย
        direct_sales = 0
        for order in orders_direct:
            if order.get('status') != 'rejected':
                direct_sales += order.get('total_amount', 0)
                print(f"Order {order.get('order_id')}: {order.get('total_amount')} บาท (status: {order.get('status')})")
        
        print(f"ยอดขายรวม (Direct): {direct_sales} บาท")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเรียกใช้ฟังก์ชันโดยตรง: {e}")
        direct_sales = 0
    
    # 2. ทดสอบการเรียกใช้ผ่าน API
    print("\n=== การเรียกใช้ผ่าน API ===")
    try:
        # เรียก API
        api_url = f"http://localhost:5000/api/dashboard-data?start_date={start_date}&end_date={end_date}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            api_period_sales = data.get('periodSales', 0)
            api_today_sales = data.get('todaySales', 0)
            api_week_sales = data.get('weekSales', 0)
            
            print(f"API Response Status: {response.status_code}")
            print(f"Period Sales (API): {api_period_sales} บาท")
            print(f"Today Sales (API): {api_today_sales} บาท")
            print(f"Week Sales (API): {api_week_sales} บาท")
            
        else:
            print(f"API Error: {response.status_code}")
            api_period_sales = 0
            
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเรียก API: {e}")
        api_period_sales = 0
    
    # 3. เปรียบเทียบผลลัพธ์
    print("\n=== เปรียบเทียบผลลัพธ์ ===")
    print(f"Direct Function: {direct_sales} บาท")
    print(f"API Response: {api_period_sales} บาท")
    
    if direct_sales == api_period_sales:
        print("✅ ผลลัพธ์ตรงกัน")
    else:
        print("❌ ผลลัพธ์ไม่ตรงกัน!")
        print(f"ความแตกต่าง: {abs(direct_sales - api_period_sales)} บาท")
        
        # ตรวจสอบเพิ่มเติม
        print("\n=== การตรวจสอบเพิ่มเติม ===")
        
        # ตรวจสอบวันนี้
        today_str = today.strftime('%Y-%m-%d')
        today_orders = db.get_orders_by_date_range(today_str, today_str)
        today_direct = sum(order.get('total_amount', 0) for order in today_orders if order.get('status') != 'rejected')
        print(f"วันนี้ (Direct): {today_direct} บาท")
        
        # ตรวจสอบสัปดาห์ปัจจุบัน (จันทร์-อาทิตย์)
        days_since_monday = today.weekday()
        week_start = (today - timedelta(days=days_since_monday)).strftime('%Y-%m-%d')
        week_end = (today + timedelta(days=6-days_since_monday)).strftime('%Y-%m-%d')
        week_orders = db.get_orders_by_date_range(week_start, week_end)
        week_direct = sum(order.get('total_amount', 0) for order in week_orders if order.get('status') != 'rejected')
        print(f"สัปดาห์ปัจจุบัน (Direct): {week_direct} บาท (จาก {week_start} ถึง {week_end})")

if __name__ == '__main__':
    test_api_vs_direct()