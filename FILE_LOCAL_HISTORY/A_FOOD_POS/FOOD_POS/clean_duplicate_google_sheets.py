#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from collections import defaultdict

# เชื่อมต่อ Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

# โหลดการตั้งค่า
with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

spreadsheet_id = config['spreadsheet_id']

print("🧹 เริ่มล้างข้อมูลซ้ำใน Google Sheets...")

# ดึงข้อมูลทั้งหมด
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='Orders!A:I'
).execute()

values = result.get('values', [])

if len(values) <= 1:
    print("ไม่มีข้อมูลที่ต้องล้าง")
    exit()

header = values[0]
data_rows = values[1:]

print(f"พบข้อมูลทั้งหมด: {len(data_rows)} แถว")

# จัดกลุ่มข้อมูลตาม Order ID
orders = defaultdict(list)
for i, row in enumerate(data_rows):
    if len(row) > 0 and row[0] and not row[0].startswith('รวม'):
        order_id = str(row[0])
        orders[order_id].append((i + 2, row))  # +2 เพราะ index เริ่มจาก 0 และมี header

print(f"พบออเดอร์ที่แตกต่างกัน: {len(orders)} ออเดอร์")

# หาออเดอร์ที่มีข้อมูลซ้ำ
duplicate_orders = {}
for order_id, rows in orders.items():
    if len(rows) > 9:  # ถ้ามีมากกว่า 9 รายการ (Order 170 ควรมี 9 รายการ)
        duplicate_orders[order_id] = rows
        print(f"Order {order_id}: พบ {len(rows)} รายการ (ควรมี 9 รายการ)")

if not duplicate_orders:
    print("ไม่พบข้อมูลซ้ำ")
    exit()

# สร้างข้อมูลใหม่ที่ไม่มีการซ้ำ
clean_data = [header]  # เริ่มด้วย header

for order_id, rows in orders.items():
    if order_id in duplicate_orders:
        # เก็บเฉพาะ 9 รายการแรก
        print(f"ล้างข้อมูลซ้ำสำหรับ Order {order_id}: เก็บ 9 รายการแรก จาก {len(rows)} รายการ")
        for i in range(min(9, len(rows))):
            clean_data.append(rows[i][1])  # [1] คือข้อมูลแถว (ไม่ใช่ index)
    else:
        # เก็บข้อมูลทั้งหมด
        for row_index, row_data in rows:
            clean_data.append(row_data)

print(f"ข้อมูลหลังล้าง: {len(clean_data) - 1} แถว (ไม่รวม header)")

# ล้างข้อมูลเก่าและเขียนข้อมูลใหม่
print("🔄 กำลังอัปเดต Google Sheets...")

# ล้างข้อมูลเก่า
service.spreadsheets().values().clear(
    spreadsheetId=spreadsheet_id,
    range='Orders!A:I'
).execute()

# เขียนข้อมูลใหม่
service.spreadsheets().values().update(
    spreadsheetId=spreadsheet_id,
    range='Orders!A1',
    valueInputOption='USER_ENTERED',
    body={'values': clean_data}
).execute()

print("✅ ล้างข้อมูลซ้ำเสร็จสิ้น!")
print(f"📊 ข้อมูลปัจจุบัน: {len(clean_data) - 1} แถว")
print(f"🔗 ตรวจสอบที่: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")

# แสดงสรุปออเดอร์ที่เหลือ
final_orders = defaultdict(int)
for row in clean_data[1:]:  # ข้าม header
    if len(row) > 0 and row[0] and not row[0].startswith('รวม'):
        order_id = str(row[0])
        final_orders[order_id] += 1

print("\n📋 สรุปออเดอร์หลังล้างข้อมูล:")
for order_id, count in sorted(final_orders.items()):
    print(f"  Order {order_id}: {count} รายการ")