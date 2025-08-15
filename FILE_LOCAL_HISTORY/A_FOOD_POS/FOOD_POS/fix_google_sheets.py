#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script สำหรับแก้ไขและสร้าง Google Sheets ที่ขาดหายไป
"""

import sys
import os

# เพิ่ม path ของ backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from google_sheets import (
    google_sheets_manager,
    is_google_sheets_enabled
)

def create_missing_sheets():
    """
    สร้าง sheets ที่ขาดหายไป
    """
    if not is_google_sheets_enabled():
        print("❌ Google Sheets ไม่ได้เปิดใช้งาน")
        return False
    
    try:
        # ดึงข้อมูล spreadsheet ปัจจุบัน
        spreadsheet = google_sheets_manager.service.spreadsheets().get(
            spreadsheetId=google_sheets_manager.spreadsheet_id
        ).execute()
        
        existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
        print(f"📋 Sheets ที่มีอยู่: {existing_sheets}")
        
        # รายการ sheets ที่ต้องการ
        required_sheets = {
            'Orders': [
                'Order ID', 'Table Number', 'Session ID', 'Status', 'Total Amount (฿)', 
                'Payment Method', 'Customer Count', 'Order Type', 'Created Date', 
                'Created Time', 'Completed Date', 'Completed Time', 'Duration (min)', 'Updated At'
            ],
            'Order_Items': [
                'Order Item ID', 'Order ID', 'Item ID', 'Category', 'Item Name', 
                'Quantity', 'Unit Price (฿)', 'Total Price (฿)', 'Discount (%)', 
                'Final Price (฿)', 'Customer Request', 'Special Options', 'Status', 'Created At'
            ],
            'Daily_Summary': [
                'Date', 'Day of Week', 'Total Orders', 'Completed Orders', 'Cancelled Orders',
                'Total Revenue (฿)', 'Total Items Sold', 'Average Order Value (฿)', 
                'Peak Hour', 'Most Popular Item', 'Total Tables Served', 
                'Average Service Time (min)', 'Updated At'
            ],
            'Monthly_Summary': [
                'Month-Year', 'Total Orders', 'Total Revenue (฿)', 'Average Daily Revenue (฿)',
                'Best Day', 'Worst Day', 'Growth Rate (%)', 'Top 3 Items', 'Updated At'
            ],
            'Item_Analytics': [
                'Item Name', 'Category', 'Total Sold', 'Total Revenue (฿)', 
                'Average Price (฿)', 'Popularity Rank', 'Last Ordered', 
                'Frequency Score', 'Profit Margin (%)', 'Updated At'
            ]
        }
        
        requests = []
        
        # สร้าง sheets ที่ขาดหายไป
        for sheet_name, headers in required_sheets.items():
            if sheet_name not in existing_sheets:
                print(f"🔄 กำลังสร้าง sheet: {sheet_name}")
                requests.append({
                    'addSheet': {
                        'properties': {
                            'title': sheet_name,
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': len(headers)
                            }
                        }
                    }
                })
        
        # ส่งคำขอสร้าง sheets
        if requests:
            response = google_sheets_manager.service.spreadsheets().batchUpdate(
                spreadsheetId=google_sheets_manager.spreadsheet_id,
                body={'requests': requests}
            ).execute()
            print(f"✅ สร้าง {len(requests)} sheets สำเร็จ")
        
        # สร้าง headers สำหรับทุก sheet
        for sheet_name, headers in required_sheets.items():
            try:
                range_name = f"{sheet_name}!A1:{chr(65 + len(headers) - 1)}1"
                body = {
                    'values': [headers]
                }
                
                google_sheets_manager.service.spreadsheets().values().update(
                    spreadsheetId=google_sheets_manager.spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body=body
                ).execute()
                print(f"✅ สร้าง headers สำหรับ {sheet_name} สำเร็จ")
                
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในการสร้าง headers สำหรับ {sheet_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้าง sheets: {e}")
        return False

def add_sample_data():
    """
    เพิ่มข้อมูลตัวอย่างตามภาพ
    """
    if not is_google_sheets_enabled():
        print("❌ Google Sheets ไม่ได้เปิดใช้งาน")
        return False
    
    try:
        # ข้อมูล Orders
        orders_data = [[
            171, 1, "session_171", "เสร็จสิ้น", 869, "เงินสด", 2, "Dine-in",
            "2025-01-10", "10:30:00", "2025-01-10", "10:45:00", 15, "2025-01-10 10:45:30"
        ]]
        
        google_sheets_manager.service.spreadsheets().values().update(
            spreadsheetId=google_sheets_manager.spreadsheet_id,
            range="Orders!A2:N2",
            valueInputOption='RAW',
            body={'values': orders_data}
        ).execute()
        print("✅ เพิ่มข้อมูล Orders สำเร็จ")
        
        # ข้อมูล Order_Items
        items_data = [
            [1, 171, 1, "เมนูข้าว", "ข้าวกะเพราทะเล", 1, 59, 59, 0, 59, "ไม่ใส่หอม", "เผ็ดน้อย", "เสร็จสิ้น", "2025-01-10 10:30:15"],
            [2, 171, 2, "เมนูข้าว", "ข้าวกะเพราหมูสับ", 1, 49, 49, 0, 49, "", "เผ็ดปานกลาง", "เสร็จสิ้น", "2025-01-10 10:30:20"],
            [3, 171, 3, "เมนูข้าว", "ข้าวกะเพราไก่", 1, 49, 49, 0, 49, "", "เผ็ดน้อย", "เสร็จสิ้น", "2025-01-10 10:30:25"],
            [4, 171, 4, "เมนูข้าว", "ข้าวปักใต้หอยลาย", 1, 49, 49, 0, 49, "ไม่เผ็ด", "", "เสร็จสิ้น", "2025-01-10 10:30:30"],
            [5, 171, 5, "เมนูข้าว", "ข้าวปักใต้ผัดพริกแกง", 1, 49, 49, 0, 49, "", "เผ็ดปานกลาง", "เสร็จสิ้น", "2025-01-10 10:30:35"],
            [6, 171, 6, "เครื่องดื่ม", "ชาลิ้ม", 1, 59, 59, 0, 59, "ไม่เรียง", "หวานน้อย", "เสร็จสิ้น", "2025-01-10 10:30:40"],
            [7, 171, 7, "เครื่องดื่ม", "ชาลิ้ม (ความหวาน)", 1, 59, 59, 0, 59, "", "หวานปานกลาง", "เสร็จสิ้น", "2025-01-10 10:30:45"],
            [8, 171, 8, "เมนูข้าว", "ข้าวกะเพราหมูสับ (เผ็ดมาก)", 1, 59, 59, 0, 59, "ไม่ใส่ผัก", "เผ็ดมาก", "เสร็จสิ้น", "2025-01-10 10:30:50"]
        ]
        
        google_sheets_manager.service.spreadsheets().values().update(
            spreadsheetId=google_sheets_manager.spreadsheet_id,
            range="Order_Items!A2:N9",
            valueInputOption='RAW',
            body={'values': items_data}
        ).execute()
        print("✅ เพิ่มข้อมูล Order_Items สำเร็จ")
        
        # ข้อมูล Daily_Summary
        daily_data = [[
            "2025-01-10", "วันศุกร์", 25, 23, 2, 2500.00, 45, 108.70,
            "12:00-13:00", "ข้าวผัดกุ้ง", 15, 18, "2025-01-10 23:59:59"
        ]]
        
        google_sheets_manager.service.spreadsheets().values().update(
            spreadsheetId=google_sheets_manager.spreadsheet_id,
            range="Daily_Summary!A2:M2",
            valueInputOption='RAW',
            body={'values': daily_data}
        ).execute()
        print("✅ เพิ่มข้อมูล Daily_Summary สำเร็จ")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเพิ่มข้อมูล: {e}")
        return False

def format_all_sheets():
    """
    จัดรูปแบบทุก sheets
    """
    if not is_google_sheets_enabled():
        print("❌ Google Sheets ไม่ได้เปิดใช้งาน")
        return False
    
    try:
        spreadsheet = google_sheets_manager.service.spreadsheets().get(
            spreadsheetId=google_sheets_manager.spreadsheet_id
        ).execute()
        
        requests = []
        
        for sheet in spreadsheet.get('sheets', []):
            sheet_id = sheet['properties']['sheetId']
            
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
            
            # ปรับขนาดคอลัมน์
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
            print("✅ จัดรูปแบบทุก sheets สำเร็จ")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดรูปแบบ: {e}")
        return False

def main():
    """
    ฟังก์ชันหลัก
    """
    print("=" * 60)
    print("🔧 Google Sheets Fixer & Data Creator")
    print("=" * 60)
    
    if not is_google_sheets_enabled():
        print("❌ Google Sheets ไม่ได้เปิดใช้งาน")
        return False
    
    print(f"✅ เชื่อมต่อ Google Sheets สำเร็จ")
    print(f"📊 Spreadsheet ID: {google_sheets_manager.spreadsheet_id}")
    print()
    
    # สร้าง sheets ที่ขาดหายไป
    print("🔄 กำลังสร้าง sheets ที่ขาดหายไป...")
    if create_missing_sheets():
        print("✅ สร้าง sheets สำเร็จ")
    
    # เพิ่มข้อมูลตัวอย่าง
    print("\n📝 กำลังเพิ่มข้อมูลตัวอย่าง...")
    if add_sample_data():
        print("✅ เพิ่มข้อมูลตัวอย่างสำเร็จ")
    
    # จัดรูปแบบ
    print("\n🎨 กำลังจัดรูปแบบ...")
    if format_all_sheets():
        print("✅ จัดรูปแบบสำเร็จ")
    
    print("\n🎉 เสร็จสิ้นการแก้ไขและสร้างข้อมูล")
    print("\n🔗 เปิด Google Sheets:")
    print(f"   https://docs.google.com/spreadsheets/d/{google_sheets_manager.spreadsheet_id}/edit")
    
    print("\n📋 ข้อมูลที่สร้าง:")
    print("   • Order ID 171 - ออเดอร์โต๊ะ 1")
    print("   • รายการอาหาร 8 รายการ (ยอดรวม 869 บาท)")
    print("   • สรุปยอดขายรายวัน")
    print("   • Headers ครบทุก sheets")
    
    print("\n" + "=" * 60)
    print("🏁 เสร็จสิ้นการดำเนินการ")
    print("=" * 60)

if __name__ == "__main__":
    main()