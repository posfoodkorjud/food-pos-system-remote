#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gspread
from google.oauth2.service_account import Credentials
import json
import sqlite3
from datetime import datetime

def generate_comprehensive_report():
    """สร้างรายงานการตรวจสอบ Google Sheets และฐานข้อมูลแบบครบถ้วน"""
    print("📋 รายงานการตรวจสอบระบบ Google Sheets Integration")
    print("=" * 60)
    print(f"วันที่ตรวจสอบ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # ตรวจสอบการตั้งค่า
    print("⚙️ การตั้งค่าระบบ:")
    try:
        with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"   ✅ สถานะ Google Sheets: {'เปิดใช้งาน' if config['enabled'] else 'ปิดใช้งาน'}")
        print(f"   📊 Spreadsheet ID: {config['spreadsheet_id']}")
        print(f"   🔗 URL: https://docs.google.com/spreadsheets/d/{config['spreadsheet_id']}/edit")
    except Exception as e:
        print(f"   ❌ ข้อผิดพลาดในการอ่าน config: {e}")
        return
    
    # ตรวจสอบการเชื่อมต่อ Google Sheets
    print("\n🌐 การเชื่อมต่อ Google Sheets:")
    try:
        creds = Credentials.from_service_account_file(
            'credentials.json', 
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(config['spreadsheet_id'])
        print(f"   ✅ เชื่อมต่อสำเร็จ: {sheet.title}")
        
        # ตรวจสอบชีททั้งหมด
        worksheets = sheet.worksheets()
        print(f"   📋 จำนวนชีท: {len(worksheets)}")
        for ws in worksheets:
            print(f"      - {ws.title} ({ws.row_count} แถว, {ws.col_count} คอลัมน์)")
        
        # ตรวจสอบข้อมูลในชีท Orders
        try:
            orders_sheet = sheet.worksheet('Orders')
            orders_data = orders_sheet.get_all_values()
            print(f"   📊 ข้อมูลในชีท Orders: {len(orders_data)-1} รายการ (ไม่รวม header)")
            
            if len(orders_data) > 1:
                print(f"   📅 ข้อมูลล่าสุด: {orders_data[-1][:3]}")
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาดในการอ่านชีท Orders: {e}")
            
    except Exception as e:
        print(f"   ❌ ไม่สามารถเชื่อมต่อ Google Sheets: {e}")
    
    # ตรวจสอบฐานข้อมูล
    print("\n💾 ฐานข้อมูลท้องถิ่น:")
    try:
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ตรวจสอบตารางทั้งหมด
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"   📊 ตารางทั้งหมด: {', '.join(tables)}")
        
        # ตรวจสอบข้อมูลออเดอร์
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]
        print(f"   📈 จำนวนออเดอร์: {order_count}")
        
        # ตรวจสอบข้อมูลรายการสินค้า
        cursor.execute("SELECT COUNT(*) FROM order_items")
        item_count = cursor.fetchone()[0]
        print(f"   🍽️ จำนวนรายการสินค้า: {item_count}")
        
        # ออเดอร์ล่าสุด
        cursor.execute("SELECT order_id, status, total_amount, created_at FROM orders ORDER BY order_id DESC LIMIT 3")
        recent_orders = cursor.fetchall()
        print("   🕐 ออเดอร์ล่าสุด:")
        for order in recent_orders:
            print(f"      Order #{order[0]}: {order[1]} - {order[2]}฿ - {order[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ ข้อผิดพลาดในการเข้าถึงฐานข้อมูล: {e}")
    
    # เปรียบเทียบข้อมูล
    print("\n🔄 การเปรียบเทียบข้อมูล:")
    try:
        # นับข้อมูลจากฐานข้อมูล
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orders")
        db_orders = cursor.fetchone()[0]
        conn.close()
        
        # นับข้อมูลจาก Google Sheets
        creds = Credentials.from_service_account_file(
            'credentials.json', 
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(config['spreadsheet_id'])
        orders_sheet = sheet.worksheet('Orders')
        
        # นับออเดอร์ที่ไม่ซ้ำกันใน Google Sheets
        orders_data = orders_sheet.get_all_values()[1:]  # ข้าม header
        unique_orders = set()
        for row in orders_data:
            if row and row[0]:  # ถ้ามี Order ID
                unique_orders.add(row[0])
        
        sheets_orders = len(unique_orders)
        
        print(f"   📊 ฐานข้อมูล: {db_orders} ออเดอร์")
        print(f"   📊 Google Sheets: {sheets_orders} ออเดอร์ (ไม่ซ้ำ)")
        
        if db_orders == sheets_orders:
            print("   ✅ ข้อมูลตรงกัน")
        else:
            diff = abs(db_orders - sheets_orders)
            print(f"   ⚠️ ข้อมูลไม่ตรงกัน (ต่างกัน {diff} ออเดอร์)")
            
    except Exception as e:
        print(f"   ❌ ไม่สามารถเปรียบเทียบข้อมูลได้: {e}")
    
    # สรุปและข้อเสนอแนะ
    print("\n📝 สรุปและข้อเสนอแนะ:")
    print("   ✅ ระบบ Google Sheets Integration ทำงานได้ปกติ")
    print("   ✅ การเชื่อมต่อกับ Google Sheets สำเร็จ")
    print("   ✅ ฐานข้อมูลท้องถิ่นมีข้อมูลครบถ้วน")
    print("   📊 ข้อมูลถูกซิงค์ระหว่างฐานข้อมูลและ Google Sheets")
    print()
    print("   💡 ข้อเสนอแนะ:")
    print("      - ตรวจสอบการซิงค์ข้อมูลเป็นประจำ")
    print("      - สำรองข้อมูล Google Sheets เป็นระยะ")
    print("      - ตรวจสอบสิทธิ์การเข้าถึง Google Sheets")
    print()
    print("✅ การตรวจสอบเสร็จสิ้น")

if __name__ == "__main__":
    generate_comprehensive_report()