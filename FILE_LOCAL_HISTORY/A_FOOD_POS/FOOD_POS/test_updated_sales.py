#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import date

def test_updated_sales_api():
    """ทดสอบ API หลังจากแก้ไขให้รวมทุกสถานะยกเว้น rejected"""
    
    base_url = "http://localhost:5000"
    
    print("=== ทดสอบ API หลังจากแก้ไข ===")
    print(f"วันที่ทดสอบ: {date.today()}")
    print()
    
    # ทดสอบ sales-summary API
    print("1. ทดสอบ /api/sales-summary")
    try:
        response = requests.get(f"{base_url}/api/sales-summary")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                sales_data = data.get('data', {})
                print(f"   วันนี้: {sales_data.get('today', {}).get('orders', 0)} ออเดอร์, {sales_data.get('today', {}).get('total', 0)} บาท")
                print(f"   สัปดาห์: {sales_data.get('week', {}).get('orders', 0)} ออเดอร์, {sales_data.get('week', {}).get('total', 0)} บาท")
                print(f"   เดือน: {sales_data.get('month', {}).get('orders', 0)} ออเดอร์, {sales_data.get('month', {}).get('total', 0)} บาท")
                print(f"   รวมทั้งหมด: {sales_data.get('total', {}).get('total', 0)} บาท")
            else:
                print(f"   Error: {data.get('error')}")
        else:
            print(f"   HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # ทดสอบ dashboard-data API
    print("2. ทดสอบ /api/dashboard-data")
    try:
        today_str = date.today().strftime('%Y-%m-%d')
        response = requests.get(f"{base_url}/api/dashboard-data?startDate={today_str}&endDate={today_str}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                dashboard_data = data.get('data', {})
                print(f"   วันนี้: {dashboard_data.get('todaySales', 0)} บาท")
                print(f"   สัปดาห์: {dashboard_data.get('weekSales', 0)} บาท")
                print(f"   เดือน: {dashboard_data.get('monthSales', 0)} บาท")
                print(f"   ช่วงที่เลือก: {dashboard_data.get('periodSales', 0)} บาท")
                print(f"   ลูกค้าทั้งหมด: {dashboard_data.get('totalCustomers', 0)} คน")
            else:
                print(f"   Error: {data.get('error')}")
        else:
            print(f"   HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # ทดสอบ top-items API
    print("3. ทดสอบ /api/top-items")
    try:
        response = requests.get(f"{base_url}/api/top-items?limit=3")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                top_items = data.get('data', [])
                print(f"   เมนูขายดี {len(top_items)} อันดับแรก:")
                for i, item in enumerate(top_items, 1):
                    print(f"     {i}. {item.get('name')}: {item.get('quantity')} จาน, {item.get('sales')} บาท")
            else:
                print(f"   Error: {data.get('error')}")
        else:
            print(f"   HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    print("=== เสร็จสิ้นการทดสอบ ===")

if __name__ == "__main__":
    test_updated_sales_api()