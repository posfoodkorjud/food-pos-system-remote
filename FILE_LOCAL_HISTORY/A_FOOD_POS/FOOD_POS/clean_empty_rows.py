#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def clean_empty_rows_in_orders():
    """ลบแถวว่างใน Orders sheet"""
    try:
        # โหลด config
        with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        spreadsheet_id = config['spreadsheet_id']
        
        # ตั้งค่า credentials
        credentials = Credentials.from_service_account_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        
        print("🔍 กำลังตรวจสอบข้อมูลใน Orders sheet...")
        
        # อ่านข้อมูลทั้งหมดจาก Orders sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Orders!A:I'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("❌ ไม่มีข้อมูลใน Orders sheet")
            return
        
        print(f"📊 พบข้อมูลทั้งหมด {len(values)} แถว")
        
        # ตรวจสอบแถวว่าง
        empty_rows = []
        clean_data = []
        
        for i, row in enumerate(values):
            row_num = i + 1
            
            # ตรวจสอบว่าแถวว่างหรือไม่ (ทุกเซลล์ว่างหรือมีแต่ช่องว่าง)
            is_empty = True
            if row:
                for cell in row:
                    if cell and str(cell).strip():
                        is_empty = False
                        break
            
            if is_empty and row_num > 1:  # ไม่ลบ header
                empty_rows.append(row_num)
                print(f"🗑️  แถวที่ {row_num}: แถวว่าง")
            else:
                clean_data.append(row)
                if row_num <= 20:  # แสดงข้อมูล 20 แถวแรก
                    first_cell = row[0] if row else ''
                    print(f"📝 แถวที่ {row_num}: {first_cell}")
        
        if empty_rows:
            print(f"\n🧹 พบแถวว่าง {len(empty_rows)} แถว: {empty_rows}")
            print("🔄 กำลังลบแถวว่าง...")
            
            # ล้างข้อมูลเก่าและเขียนข้อมูลใหม่
            service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range='Orders!A:I'
            ).execute()
            
            # เขียนข้อมูลที่สะอาดแล้ว
            if clean_data:
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range='Orders!A1',
                    valueInputOption='USER_ENTERED',
                    body={'values': clean_data}
                ).execute()
            
            print(f"✅ ลบแถวว่างเสร็จสิ้น!")
            print(f"📊 ข้อมูลหลังทำความสะอาด: {len(clean_data)} แถว")
            
        else:
            print("✅ ไม่พบแถวว่างใน Orders sheet")
        
        # แสดงข้อมูลแถวที่ 8-13 โดยเฉพาะ
        print("\n🔍 ตรวจสอบแถวที่ 8-13:")
        for i in range(7, 13):  # แถว 8-13 (index 7-12)
            if i < len(clean_data):
                row = clean_data[i]
                first_cell = row[0] if row else ''
                second_cell = row[1] if len(row) > 1 else ''
                print(f"  แถวที่ {i+1}: '{first_cell}' | '{second_cell}'")
            else:
                print(f"  แถวที่ {i+1}: ไม่มีข้อมูล")
        
        print(f"\n🔗 ตรวจสอบผลลัพธ์ที่: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    clean_empty_rows_in_orders()