#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from google.oauth2.service_account import Credentials
import gspread

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

print("🔍 ตรวจสอบข้อมูลในคอลัมน์คำขอพิเศษและหมายเหตุ...")

# ดึงข้อมูลทั้งหมดจาก Google Sheets
all_data = sheet.get_all_values()

print(f"\n📊 ตัวอย่างข้อมูลในคอลัมน์ต่างๆ:")
print(f"Header: {all_data[0]}")
print(f"\n🎯 ตัวอย่างข้อมูล 10 แถวแรก:")

for i, row in enumerate(all_data[1:11], start=2):  # แสดง 10 แถวแรก
    if len(row) >= 9:
        order_id = row[0]
        item_name = row[2]
        special_request = row[6]
        notes = row[7]
        
        print(f"แถว {i}: Order {order_id}")
        print(f"  ชื่อสินค้า: {item_name}")
        print(f"  คำขอพิเศษ: '{special_request}'")
        print(f"  หมายเหตุ: '{notes}'")
        print()

# ตรวจสอบข้อมูลจากฐานข้อมูลเพื่อเปรียบเทียบ
conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

print(f"\n🔍 ตรวจสอบข้อมูล customer_request จากฐานข้อมูล:")
cursor.execute('''
    SELECT o.order_id, mi.name, oi.customer_request
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN menu_items mi ON oi.item_id = mi.item_id
    WHERE o.status = 'completed' AND oi.customer_request IS NOT NULL AND oi.customer_request != ''
    ORDER BY o.order_id DESC
    LIMIT 10
''')

db_data = cursor.fetchall()
print(f"\n📋 ข้อมูล customer_request จากฐานข้อมูล (10 รายการแรก):")
for item in db_data:
    order_id, item_name, customer_request = item
    print(f"Order {order_id}: {item_name}")
    print(f"  customer_request: '{customer_request}'")
    print()

conn.close()
print("✅ ตรวจสอบเสร็จสิ้น")