#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script สำหรับสร้างข้อมูลตัวอย่างใน Google Sheets
ตามรูปแบบที่แสดงในภาพ
"""

import sys
import os
from datetime import datetime, timedelta

# เพิ่ม path ของ backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from google_sheets import (
    google_sheets_manager,
    is_google_sheets_enabled
)

def create_sample_orders_data():
    """
    สร้างข้อมูลตัวอย่างสำหรับ Orders sheet ตามภาพที่แนบมา
    """
    if not is_google_sheets_enabled():
        print("❌ Google Sheets ไม่ได้เปิดใช้งาน")
        return False
    
    try:
        # ข้อมูลตัวอย่างตามภาพ (Order ID 171)
        sample_data = [
            [
                171,  # Order ID
                1,    # Table Number
                "session_171",  # Session ID
                "เสร็จสิ้น",  # Status
                869,  # Total Amount
                "เงินสด",  # Payment Method
                2,    # Customer Count
                "Dine-in",  # Order Type
                "2025-01-10",  # Created Date
                "10:30:00",   # Created Time
                "2025-01-10",  # Completed Date
                "10:45:00",   # Completed Time
                15,   # Duration (min)
                "2025-01-10 10:45:30"  # Updated At
            ]
        ]
        
        # เขียนข้อมูลลง Orders sheet
        range_name = "Orders!A2:N2"
        body = {
            'values': sample_data
        }
        
        result = google_sheets_manager.service.spreadsheets().values().update(
            spreadsheetId=google_sheets_manager.spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"✅ เพิ่มข้อมูล Orders สำเร็จ: {result.get('updatedCells')} เซลล์")
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้างข้อมูล Orders: {e}")
        return False

def create_sample_order_items_data():
    """
    สร้างข้อมูลตัวอย่างสำหรับ Order_Items sheet ตามภาพที่แนบมา
    """
    if not is_google_sheets_enabled():
        print("❌ Google Sheets ไม่ได้เปิดใช้งาน")
        return False
    
    try:
        # ข้อมูลรายการอาหารตามภาพ
        sample_items = [
            [1, 171, 1, "เมนูข้าว", "ข้าวกะเพราทะเล", 1, 59, 59, 0, 59, "ไม่ใส่หอม", "เผ็ดน้อย", "เสร็จสิ้น", "2025-01-10 10:30:15"],
            [2, 171, 2, "เมนูข้าว", "ข้าวกะเพราหมูสับ", 1, 49, 49, 0, 49, "", "เผ็ดปานกลาง", "เสร็จสิ้น", "2025-01-10 10:30:20"],
            [3, 171, 3, "เมนูข้าว", "ข้าวกะเพราไก่", 1, 49, 49, 0, 49, "", "เผ็ดน้อย", "เสร็จสิ้น", "2025-01-10 10:30:25"],
            [4, 171, 4, "เมนูข้าว", "ข้าวปักใต้หอยลาย", 1, 49, 49, 0, 49, "ไม่เผ็ด", "", "เสร็จสิ้น", "2025-01-10 10:30:30"],
            [5, 171, 5, "เมนูข้าว", "ข้าวปักใต้ผัดพริกแกง", 1, 49, 49, 0, 49, "", "เผ็ดปานกลาง", "เสร็จสิ้น", "2025-01-10 10:30:35"],
            [6, 171, 6, "เครื่องดื่ม", "ชาลิ้ม", 1, 59, 59, 0, 59, "ไม่เรียง", "หวานน้อย", "เสร็จสิ้น", "2025-01-10 10:30:40"],
            [7, 171, 7, "เครื่องดื่ม", "ชาลิ้ม (ความหวาน)", 1, 59, 59, 0, 59, "", "หวานปานกลาง", "เสร็จสิ้น", "2025-01-10 10:30:45"],
            [8, 171, 8, "เมนูข้าว", "ข้าวกะเพราหมูสับ (เผ็ดมาก)", 1, 59, 59, 0, 59, "ไม่ใส่ผัก", "เผ็ดมาก", "เสร็จสิ้น", "2025-01-10 10:30:50"]
        ]
        
        # เขียนข้อมูลลง Order_Items sheet
        range_name = "Order_Items!A2:N9"
        body = {
            'values': sample_items
        }
        
        result = google_sheets_manager.service.spreadsheets().values().update(
            spreadsheetId=google_sheets_manager.spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"✅ เพิ่มข้อมูล Order_Items สำเร็จ: {result.get('updatedCells')} เซลล์")
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้างข้อมูล Order_Items: {e}")
        return False

def create_sample_daily_summary():
    """
    สร้างข้อมูลตัวอย่างสำหรับ Daily_Summary sheet
    """
    if not is_google_sheets_enabled():
        print("❌ Google Sheets ไม่ได้เปิดใช้งาน")
        return False
    
    try:
        # ข้อมูลสรุปรายวัน
        today = datetime.now().strftime("%Y-%m-%d")
        sample_data = [
            [
                today,  # Date
                "วันศุกร์",  # Day of Week
                25,     # Total Orders
                23,     # Completed Orders
                2,      # Cancelled Orders
                2500.00,  # Total Revenue
                45,     # Total Items Sold
                108.70,   # Average Order Value
                "12:00-13:00",  # Peak Hour
                "ข้าวผัดกุ้ง",   # Most Popular Item
                15,     # Total Tables Served
                18,     # Average Service Time
                f"{today} 23:59:59"  # Updated At
            ]
        ]
        
        # เขียนข้อมูลลง Daily_Summary sheet
        range_name = "Daily_Summary!A2:M2"
        body = {
            'values': sample_data
        }
        
        result = google_sheets_manager.service.spreadsheets().values().update(
            spreadsheetId=google_sheets_manager.spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"✅ เพิ่มข้อมูล Daily_Summary สำเร็จ: {result.get('updatedCells')} เซลล์")
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้างข้อมูล Daily_Summary: {e}")
        return False

def format_sheets():
    """
    จัดรูปแบบ sheets ให้สวยงาม
    """
    if not is_google_sheets_enabled():
        print("❌ Google Sheets ไม่ได้เปิดใช้งาน")
        return False
    
    try:
        # ดึงข้อมูล spreadsheet
        spreadsheet = google_sheets_manager.service.spreadsheets().get(
            spreadsheetId=google_sheets_manager.spreadsheet_id
        ).execute()
        
        sheets = spreadsheet.get('sheets', [])
        requests = []
        
        for sheet in sheets:
            sheet_id = sheet['properties']['sheetId']
            sheet_title = sheet['properties']['title']
            
            # จัดรูปแบบหัวตาราง
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {
                                'red': 0.2,
                                'green': 0.6,
                                'blue': 0.9
                            },
                            'textFormat': {
                                'foregroundColor': {
                                    'red': 1.0,
                                    'green': 1.0,
                                    'blue': 1.0
                                },
                                'fontSize': 11,
                                'bold': True
                            },
                            'horizontalAlignment': 'CENTER'
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
                }
            })
            
            # ปรับขนาดคอลัมน์อัตโนมัติ
            requests.append({
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 20
                    }
                }
            })
        
        if requests:
            google_sheets_manager.service.spreadsheets().batchUpdate(
                spreadsheetId=google_sheets_manager.spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
        print("✅ จัดรูปแบบ sheets สำเร็จ")
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดรูปแบบ: {e}")
        return False

def main():
    """
    ฟังก์ชันหลักสำหรับสร้างข้อมูลตัวอย่าง
    """
    print("=" * 60)
    print("📊 Google Sheets Sample Data Creator")
    print("=" * 60)
    
    # ตรวจสอบการเชื่อมต่อ
    if not is_google_sheets_enabled():
        print("❌ Google Sheets ไม่ได้เปิดใช้งานหรือไม่สามารถเชื่อมต่อได้")
        return False
    
    print(f"✅ เชื่อมต่อ Google Sheets สำเร็จ")
    print(f"📊 Spreadsheet ID: {google_sheets_manager.spreadsheet_id}")
    print()
    
    print("🔄 กำลังสร้างข้อมูลตัวอย่าง...")
    
    # สร้างข้อมูลตัวอย่าง
    success_count = 0
    
    if create_sample_orders_data():
        success_count += 1
    
    if create_sample_order_items_data():
        success_count += 1
    
    if create_sample_daily_summary():
        success_count += 1
    
    # จัดรูปแบบ
    if format_sheets():
        success_count += 1
    
    print()
    if success_count >= 3:
        print("✅ สร้างข้อมูลตัวอย่างสำเร็จ")
        print("\n📋 ข้อมูลที่สร้าง:")
        print("   • Order ID 171 - ออเดอร์โต๊ะ 1")
        print("   • รายการอาหาร 8 รายการ")
        print("   • ยอดรวม 869 บาท")
        print("   • สรุปยอดขายรายวัน")
        print("\n🔗 เปิด Google Sheets:")
        print(f"   https://docs.google.com/spreadsheets/d/{google_sheets_manager.spreadsheet_id}/edit")
    else:
        print("⚠️  สร้างข้อมูลตัวอย่างไม่สมบูรณ์")
    
    print("\n" + "=" * 60)
    print("🏁 เสร็จสิ้นการดำเนินการ")
    print("=" * 60)

if __name__ == "__main__":
    main()