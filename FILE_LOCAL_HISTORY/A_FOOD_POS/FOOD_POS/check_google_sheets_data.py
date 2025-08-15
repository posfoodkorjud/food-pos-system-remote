#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# เชื่อมต่อ Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

# โหลดการตั้งค่า
with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

spreadsheet_id = config['spreadsheet_id']

# ดึงข้อมูลจาก Google Sheets
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='Orders!A:I'
).execute()

values = result.get('values', [])

print(f'จำนวนแถวทั้งหมดใน Google Sheets: {len(values)}')
print(f'URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit')

if len(values) > 1:
    print('\nหัวตาราง:')
    print(values[0])
    
    print('\n10 แถวล่าสุด:')
    start_idx = max(1, len(values) - 10)  # เริ่มจากแถวที่ 1 (ข้าม header)
    for i in range(start_idx, len(values)):
        row = values[i]
        print(f'แถว {i+1}: {row}')
    
    # นับจำนวน Order ID ที่ซ้ำ
    order_ids = []
    for i in range(1, len(values)):  # ข้าม header
        if len(values[i]) > 0:
            order_ids.append(values[i][0])
    
    from collections import Counter
    order_count = Counter(order_ids)
    
    print(f'\nสรุปจำนวน Order ID:')
    for order_id, count in order_count.most_common(10):
        print(f'Order {order_id}: {count} รายการ')
    
    # ตรวจสอบ Order 170 โดยเฉพาะ
    order_170_rows = []
    for i in range(1, len(values)):
        if len(values[i]) > 0 and str(values[i][0]) == '170':
            order_170_rows.append((i+1, values[i]))
    
    print(f'\nOrder 170 ใน Google Sheets ({len(order_170_rows)} รายการ):')
    for row_num, row_data in order_170_rows:
        item_name = row_data[2] if len(row_data) > 2 else 'ไม่ระบุ'
        quantity = row_data[3] if len(row_data) > 3 else 'ไม่ระบุ'
        total_price = row_data[5] if len(row_data) > 5 else 'ไม่ระบุ'
        print(f'  แถว {row_num}: {item_name} - จำนวน: {quantity}, ราคา: {total_price}')
else:
    print('ไม่มีข้อมูลใน Google Sheets')