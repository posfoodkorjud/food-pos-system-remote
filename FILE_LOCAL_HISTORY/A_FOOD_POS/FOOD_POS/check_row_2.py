#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gspread
from google.oauth2.service_account import Credentials
import json

# โหลดการตั้งค่า Google Sheets
with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# เชื่อมต่อ Google Sheets
creds = Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
client = gspread.authorize(creds)
sheet = client.open_by_key(config['spreadsheet_id']).worksheet('Orders')

# ดึงข้อมูลทั้งหมด
data = sheet.get_all_values()

print(f"จำนวนแถวทั้งหมด: {len(data)}")
print(f"\nแถวที่ 1 (Header): {data[0] if len(data) > 0 else 'ไม่มีข้อมูล'}")
print(f"\nแถวที่ 2: {data[1] if len(data) > 1 else 'ไม่มีข้อมูล'}")

if len(data) > 2:
    print(f"\nแถวที่ 3: {data[2]}")

# ตรวจสอบข้อมูลแถวที่ 2 โดยละเอียด
if len(data) > 1:
    row_2 = data[1]
    print(f"\n🔍 วิเคราะห์แถวที่ 2:")
    print(f"   Order ID: {row_2[0] if len(row_2) > 0 else 'ไม่มี'}")
    print(f"   วันที่: {row_2[1] if len(row_2) > 1 else 'ไม่มี'}")
    print(f"   รายการ: {row_2[2] if len(row_2) > 2 else 'ไม่มี'}")
    print(f"   จำนวน: {row_2[3] if len(row_2) > 3 else 'ไม่มี'}")
    print(f"   ราคา: {row_2[4] if len(row_2) > 4 else 'ไม่มี'}")
    
    # ตรวจสอบวันที่ที่แปลกๆ
    if len(row_2) > 1 and '1899' in str(row_2[1]):
        print(f"\n⚠️  พบวันที่ผิดปกติ: {row_2[1]}")
        print(f"   นี่อาจเป็นปัญหาจากการแปลงวันที่ที่ไม่ถูกต้อง")