#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime

def check_sync_status():
    """ตรวจสอบสถานะการซิงค์ข้อมูลระหว่างฐานข้อมูลและ Google Sheets"""
    print("🔄 ตรวจสอบสถานะการซิงค์ข้อมูล")
    print("=" * 50)
    
    try:
        # เชื่อมต่อฐานข้อมูล
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ดึงข้อมูลออเดอร์จากฐานข้อมูล
        cursor.execute("SELECT order_id, status, total_amount, created_at FROM orders ORDER BY order_id DESC")
        db_orders = cursor.fetchall()
        db_order_ids = [str(row[0]) for row in db_orders]
        
        print(f"📊 ออเดอร์ในฐานข้อมูล: {len(db_orders)}")
        
        # เชื่อมต่อ Google Sheets
        creds = Credentials.from_service_account_file(
            'credentials.json', 
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        gc = gspread.authorize(creds)
        
        with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        sheet = gc.open_by_key(config['spreadsheet_id'])
        orders_sheet = sheet.worksheet('Orders')
        sheets_data = orders_sheet.get_all_values()[1:]  # ข้าม header
        
        # หาออเดอร์ที่ไม่ซ้ำใน Google Sheets
        sheets_orders = list(set([row[0] for row in sheets_data if row and row[0]]))
        
        print(f"📊 ออเดอร์ใน Google Sheets: {len(sheets_orders)} (ไม่ซ้ำ)")
        print(f"📊 รายการทั้งหมดใน Google Sheets: {len(sheets_data)}")
        
        # หาออเดอร์ที่ยังไม่ได้ซิงค์
        missing_in_sheets = [oid for oid in db_order_ids if oid not in sheets_orders]
        extra_in_sheets = [oid for oid in sheets_orders if oid not in db_order_ids]
        
        print(f"\n🔍 ผลการเปรียบเทียบ:")
        print(f"   ❌ ออเดอร์ที่ยังไม่ได้ซิงค์ไป Google Sheets: {len(missing_in_sheets)}")
        print(f"   ⚠️ ออเดอร์ใน Google Sheets ที่ไม่มีในฐานข้อมูล: {len(extra_in_sheets)}")
        
        if missing_in_sheets:
            print(f"\n📋 ออเดอร์ที่ยังไม่ได้ซิงค์ (10 รายการแรก):")
            for i, oid in enumerate(missing_in_sheets[:10], 1):
                # หาข้อมูลออเดอร์จากฐานข้อมูล
                order_info = next((order for order in db_orders if str(order[0]) == oid), None)
                if order_info:
                    print(f"   {i}. Order #{oid}: {order_info[1]} - {order_info[2]}฿ - {order_info[3]}")
        
        if extra_in_sheets:
            print(f"\n⚠️ ออเดอร์ใน Google Sheets ที่ไม่มีในฐานข้อมูล (5 รายการแรก):")
            for i, oid in enumerate(extra_in_sheets[:5], 1):
                print(f"   {i}. Order #{oid}")
        
        # ตรวจสอบออเดอร์ล่าสุด
        print(f"\n🕐 ออเดอร์ล่าสุดในฐานข้อมูล:")
        for i, order in enumerate(db_orders[:5], 1):
            sync_status = "✅ ซิงค์แล้ว" if str(order[0]) in sheets_orders else "❌ ยังไม่ซิงค์"
            print(f"   {i}. Order #{order[0]}: {order[1]} - {sync_status}")
        
        # ตรวจสอบสถานะออเดอร์
        cursor.execute("SELECT status, COUNT(*) FROM orders GROUP BY status")
        status_counts = cursor.fetchall()
        print(f"\n📊 สถานะออเดอร์ในฐานข้อมูล:")
        for status, count in status_counts:
            print(f"   {status}: {count} รายการ")
        
        # แนะนำการแก้ไข
        print(f"\n💡 ข้อเสนอแนะ:")
        if missing_in_sheets:
            print(f"   🔧 ควรซิงค์ออเดอร์ที่ขาดหายไป Google Sheets")
            print(f"   📝 ใช้คำสั่ง: python sync_missing_orders.py")
        
        if len(missing_in_sheets) == 0 and len(extra_in_sheets) == 0:
            print(f"   ✅ ข้อมูลซิงค์ครบถ้วนแล้ว")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ ข้อผิดพลาด: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_sync_status()