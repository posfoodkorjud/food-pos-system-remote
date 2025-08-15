#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับคืนค่าเดิมของ Google Sheets จากไฟล์สำรอง
"""

import gspread
from google.oauth2.service_account import Credentials
import json
import time
from datetime import datetime

def restore_google_sheets_from_backup():
    """
    คืนค่าเดิมของ Google Sheets จากไฟล์สำรอง
    """
    print("=" * 60)
    print("🔄 Google Sheets Restore Tool")
    print("=" * 60)
    
    # โหลดการตั้งค่า Google Sheets
    try:
        with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ ไม่พบไฟล์ google_sheets_config.json")
        return False
    
    # ตั้งค่า credentials
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        client = gspread.authorize(creds)
    except FileNotFoundError:
        print("❌ ไม่พบไฟล์ credentials.json")
        return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
        return False
    
    # โหลดข้อมูลสำรอง
    backup_file = 'sheets_backups/sheets_data_20250812_132738.json'
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        print(f"✅ โหลดไฟล์สำรองสำเร็จ: {backup_file}")
    except FileNotFoundError:
        print(f"❌ ไม่พบไฟล์สำรอง: {backup_file}")
        return False
    
    # เปิด Google Sheets
    try:
        sheet = client.open_by_key(config['spreadsheet_id'])
        worksheet = sheet.worksheet('Orders')
        print(f"✅ เชื่อมต่อ Google Sheets สำเร็จ")
        print(f"📊 Spreadsheet ID: {config['spreadsheet_id']}")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเปิด Google Sheets: {e}")
        return False
    
    # แสดงข้อมูลสำรอง
    original_data = backup_data['data']
    print(f"\n📋 ข้อมูลสำรองที่พบ:")
    print(f"   - จำนวนแถวทั้งหมด: {len(original_data)}")
    print(f"   - Header: {original_data[0] if original_data else 'ไม่มี'}")
    
    # ยืนยันการคืนค่า
    print("\n⚠️  การดำเนินการนี้จะลบข้อมูลปัจจุบันทั้งหมดและคืนค่าเดิม")
    confirm = input("คุณต้องการดำเนินการต่อหรือไม่? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ ยกเลิกการคืนค่าเดิม")
        return False
    
    try:
        # ล้างข้อมูลเก่า
        print("\n🗑️  กำลังล้างข้อมูลเก่า...")
        worksheet.clear()
        time.sleep(2)  # หน่วงเวลาเพื่อหลีกเลี่ยง rate limit
        
        # คืนค่าข้อมูลเดิม
        print(f"📝 กำลังคืนค่าข้อมูลเดิม {len(original_data)} แถว...")
        
        # แบ่งข้อมูลเป็นชุดเล็กๆ เพื่อหลีกเลี่ยง quota limit
        batch_size = 100
        for i in range(0, len(original_data), batch_size):
            batch_data = original_data[i:i+batch_size]
            start_row = i + 1
            end_row = start_row + len(batch_data) - 1
            
            print(f"   กำลังเขียนแถว {start_row}-{end_row}...")
            
            # เขียนข้อมูลแบบ batch
            range_name = f'A{start_row}:I{end_row}'
            worksheet.update(values=batch_data, range_name=range_name)
            
            # หน่วงเวลาระหว่าง batch
            if i + batch_size < len(original_data):
                time.sleep(1)
        
        print("\n✅ คืนค่าข้อมูลเดิมสำเร็จ!")
        print(f"\n📊 สรุปการคืนค่า:")
        print(f"   - จำนวนแถวที่คืนค่า: {len(original_data)}")
        print(f"   - เวลาที่คืนค่า: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   - ไฟล์สำรองที่ใช้: {backup_file}")
        
        print(f"\n🔗 เปิด Google Sheets:")
        print(f"   https://docs.google.com/spreadsheets/d/{config['spreadsheet_id']}/edit")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการคืนค่าข้อมูล: {e}")
        return False

def main():
    """
    ฟังก์ชันหลัก
    """
    success = restore_google_sheets_from_backup()
    
    if success:
        print("\n🎉 การคืนค่าเดิมเสร็จสิ้น")
        print("\n📋 ข้อมูลที่คืนค่าแล้ว:")
        print("   ✓ ข้อมูล Order ทั้งหมดตามเดิม")
        print("   ✓ รูปแบบตารางเดิม")
        print("   ✓ Header และโครงสร้างเดิม")
        print("   ✓ แถวสรุปและแถวว่างตามเดิม")
    else:
        print("\n❌ การคืนค่าเดิมล้มเหลว")
        print("กรุณาตรวจสอบ:")
        print("   - ไฟล์ credentials.json")
        print("   - ไฟล์ google_sheets_config.json")
        print("   - ไฟล์สำรอง sheets_data_20250812_132738.json")
        print("   - การเชื่อมต่ออินเทอร์เน็ต")

if __name__ == '__main__':
    main()