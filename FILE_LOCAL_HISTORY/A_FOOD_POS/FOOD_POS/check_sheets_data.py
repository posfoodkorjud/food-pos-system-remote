#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime

def check_google_sheets_data():
    """ตรวจสอบข้อมูลใน Google Sheets"""
    print("🔍 กำลังตรวจสอบข้อมูล Google Sheets...")
    print("=" * 50)
    
    try:
        # เชื่อมต่อ Google Sheets
        creds = Credentials.from_service_account_file(
            'credentials.json', 
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        gc = gspread.authorize(creds)
        
        # โหลด config
        with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # เปิด spreadsheet
        sheet = gc.open_by_key(config['spreadsheet_id'])
        
        print(f"📊 ชื่อ Spreadsheet: {sheet.title}")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{config['spreadsheet_id']}/edit")
        print(f"⚙️ สถานะ: {'เปิดใช้งาน' if config['enabled'] else 'ปิดใช้งาน'}")
        print()
        
        # แสดงรายการชีททั้งหมด
        print("📋 ชีทที่มีอยู่:")
        worksheets = sheet.worksheets()
        for i, ws in enumerate(worksheets, 1):
            print(f"  {i}. {ws.title} ({ws.row_count} แถว, {ws.col_count} คอลัมน์)")
        print()
        
        # ตรวจสอบข้อมูลในแต่ละชีท
        for sheet_name in ['Orders', 'Order_Items', 'Daily_Summary']:
            try:
                ws = sheet.worksheet(sheet_name)
                data = ws.get_all_values()
                
                print(f"📊 ข้อมูลใน {sheet_name}:")
                print(f"   จำนวนแถวทั้งหมด: {len(data)}")
                
                if data:
                    print(f"   Header: {data[0]}")
                    if len(data) > 1:
                        print(f"   แถวล่าสุด: {data[-1]}")
                        print(f"   ตัวอย่างข้อมูล 3 แถวแรก:")
                        for i, row in enumerate(data[1:4], 1):
                            print(f"     แถว {i}: {row[:5]}{'...' if len(row) > 5 else ''}")
                    else:
                        print("   ไม่มีข้อมูล (มีเฉพาะ header)")
                else:
                    print("   ชีทว่าง")
                print()
                
            except gspread.WorksheetNotFound:
                print(f"❌ ไม่พบชีท '{sheet_name}'")
                print()
        
        # ตรวจสอบข้อมูลสถิติ
        try:
            orders_sheet = sheet.worksheet('Orders')
            orders_data = orders_sheet.get_all_values()
            
            if len(orders_data) > 1:
                total_orders = len(orders_data) - 1  # ลบ header
                print(f"📈 สถิติโดยรวม:")
                print(f"   จำนวนออเดอร์ทั้งหมด: {total_orders}")
                
                # นับออเดอร์วันนี้
                today = datetime.now().strftime('%Y-%m-%d')
                today_orders = 0
                for row in orders_data[1:]:
                    if len(row) > 1 and today in row[1]:  # สมมติว่าคอลัมน์ที่ 2 เป็นวันที่
                        today_orders += 1
                
                print(f"   ออเดอร์วันนี้ ({today}): {today_orders}")
                
                # แสดงออเดอร์ล่าสุด 5 รายการ
                print(f"\n🕐 ออเดอร์ล่าสุด 5 รายการ:")
                recent_orders = orders_data[-5:] if len(orders_data) > 5 else orders_data[1:]
                for i, order in enumerate(reversed(recent_orders), 1):
                    if order and len(order) >= 3:
                        print(f"   {i}. Order #{order[0]} - {order[1]} - {order[2] if len(order) > 2 else 'N/A'}")
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการวิเคราะห์สถิติ: {e}")
        
        print("\n✅ การตรวจสอบเสร็จสิ้น")
        
    except Exception as e:
        print(f"❌ ข้อผิดพลาด: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_google_sheets_data()