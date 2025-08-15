#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script สำหรับลบแผ่นงานที่ไม่ต้องการใน Google Sheets
เก็บเฉพาะแผ่นงาน Orders
"""

import sys
import os

# เพิ่ม path ของ backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from google_sheets import (
    is_google_sheets_enabled,
    google_sheets_manager
)

def delete_unwanted_sheets():
    """
    ลบแผ่นงานที่ไม่ต้องการ เก็บเฉพาะ Orders
    """
    if not is_google_sheets_enabled():
        print("❌ Google Sheets ไม่ได้เปิดใช้งาน")
        return False
    
    try:
        # ดึงข้อมูล spreadsheet ปัจจุบัน
        spreadsheet = google_sheets_manager.service.spreadsheets().get(
            spreadsheetId=google_sheets_manager.spreadsheet_id
        ).execute()
        
        existing_sheets = spreadsheet.get('sheets', [])
        print(f"📋 Sheets ที่มีอยู่:")
        for sheet in existing_sheets:
            sheet_name = sheet['properties']['title']
            sheet_id = sheet['properties']['sheetId']
            print(f"   - {sheet_name} (ID: {sheet_id})")
        
        # หาแผ่นงานที่ต้องลบ (ทุกอันยกเว้น Orders)
        sheets_to_delete = []
        orders_sheet_exists = False
        
        for sheet in existing_sheets:
            sheet_name = sheet['properties']['title']
            sheet_id = sheet['properties']['sheetId']
            
            if sheet_name == 'Orders':
                orders_sheet_exists = True
                print(f"✅ เก็บแผ่นงาน: {sheet_name}")
            else:
                sheets_to_delete.append({
                    'name': sheet_name,
                    'id': sheet_id
                })
                print(f"🗑️  จะลบแผ่นงาน: {sheet_name}")
        
        if not orders_sheet_exists:
            print("⚠️  ไม่พบแผ่นงาน Orders")
            return False
        
        if not sheets_to_delete:
            print("✅ มีเฉพาะแผ่นงาน Orders อยู่แล้ว ไม่ต้องลบอะไร")
            return True
        
        # ยืนยันการลบ
        print(f"\n⚠️  คุณต้องการลบแผ่นงาน {len(sheets_to_delete)} แผ่น ใช่หรือไม่?")
        for sheet in sheets_to_delete:
            print(f"   - {sheet['name']}")
        
        confirm = input("\nพิมพ์ 'yes' เพื่อยืนยัน: ").strip().lower()
        if confirm != 'yes':
            print("❌ ยกเลิกการลบ")
            return False
        
        # ลบแผ่นงานทีละแผ่น
        requests = []
        for sheet in sheets_to_delete:
            requests.append({
                'deleteSheet': {
                    'sheetId': sheet['id']
                }
            })
        
        if requests:
            # ส่งคำขอลบแผ่นงาน
            body = {
                'requests': requests
            }
            
            response = google_sheets_manager.service.spreadsheets().batchUpdate(
                spreadsheetId=google_sheets_manager.spreadsheet_id,
                body=body
            ).execute()
            
            print(f"\n✅ ลบแผ่นงานสำเร็จ {len(sheets_to_delete)} แผ่น")
            for sheet in sheets_to_delete:
                print(f"   ✓ ลบ: {sheet['name']}")
            
            print(f"\n🎉 เหลือเฉพาะแผ่นงาน Orders แล้ว")
            return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def main():
    """
    ฟังก์ชันหลัก
    """
    print("=" * 60)
    print("🗑️  Google Sheets - ลบแผ่นงานที่ไม่ต้องการ")
    print("=" * 60)
    
    if not is_google_sheets_enabled():
        print("❌ Google Sheets ไม่ได้เปิดใช้งานหรือไม่สามารถเชื่อมต่อได้")
        print("กรุณาตรวจสอบ:")
        print("1. ไฟล์ credentials.json")
        print("2. ไฟล์ google_sheets_config.json")
        print("3. การตั้งค่า Google Sheets API")
        return False
    
    print(f"✅ เชื่อมต่อ Google Sheets สำเร็จ")
    print(f"📊 Spreadsheet ID: {google_sheets_manager.spreadsheet_id}")
    print()
    
    # ลบแผ่นงานที่ไม่ต้องการ
    if delete_unwanted_sheets():
        print("\n🔗 เปิด Google Sheets:")
        print(f"   https://docs.google.com/spreadsheets/d/{google_sheets_manager.spreadsheet_id}/edit")
        return True
    else:
        print("\n❌ การลบแผ่นงานไม่สำเร็จ")
        return False

if __name__ == "__main__":
    main()