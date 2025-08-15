#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime

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

# เชื่อมต่อฐานข้อมูล
conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

# ดึงข้อมูล Order 170 ทั้งหมดจากฐานข้อมูล (เรียงตามเวลา)
cursor.execute('''
    SELECT oi.order_item_id, oi.order_id, mi.name, oi.quantity, oi.total_price, 
           oi.created_at, oi.status, oi.customer_request
    FROM order_items oi 
    JOIN menu_items mi ON oi.item_id = mi.item_id 
    WHERE oi.order_id = 170 
    ORDER BY oi.created_at
''')

items = cursor.fetchall()
print(f'พบ Order 170 ในฐานข้อมูล: {len(items)} รายการ')

# ลบข้อมูล Order 170 เก่าออกจาก Google Sheets
all_data = sheet.get_all_values()
header = all_data[0] if all_data else []
filtered_data = [header]  # เก็บ header

# เก็บเฉพาะข้อมูลที่ไม่ใช่ Order 170
for row in all_data[1:]:
    if row and row[0] != '170':  # ไม่ใช่ Order 170
        filtered_data.append(row)

print(f'ลบข้อมูล Order 170 เก่าออกจาก Google Sheets')

# เพิ่มข้อมูล Order 170 ใหม่ทั้งหมด
for item in items:
    order_id = str(item[1])
    created_at = datetime.strptime(item[5], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
    item_name = item[2]
    quantity = str(item[3])
    unit_price = str(int(item[4] / item[3]))  # ราคาต่อหน่วย
    total_price = str(int(item[4]))  # ราคารวม
    customer_request = item[7] or ''
    status = item[6]
    
    new_row = [order_id, created_at, item_name, quantity, unit_price, total_price, customer_request, customer_request, status]
    filtered_data.append(new_row)
    print(f'เพิ่ม: {item_name} - {quantity} x {unit_price} = {total_price} บาท')

# อัปเดต Google Sheets
sheet.clear()
if filtered_data:
    sheet.update(range_name='A1', values=filtered_data)

print(f'\n✅ อัปเดต Google Sheets เสร็จสิ้น!')
print(f'📊 ข้อมูลทั้งหมด: {len(filtered_data)-1} รายการ (ไม่รวม header)')
print(f'🍽️ Order 170: {len(items)} รายการ รวม {sum(item[4] for item in items)} บาท')

# แสดงรายการ Order 170 ที่อัปเดต
print('\n📋 รายการ Order 170 ที่อัปเดตใน Google Sheets:')
for i, item in enumerate(items, 1):
    print(f'{i:2d}. {item[2]:<30} - {item[3]} x {int(item[4]/item[3])} = {int(item[4])} บาท')

conn.close()