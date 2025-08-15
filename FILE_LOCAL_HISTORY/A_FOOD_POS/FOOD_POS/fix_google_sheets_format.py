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

print("🔧 กำลังแก้ไขรูปแบบ Google Sheets...")

# สร้าง header ใหม่ที่ถูกต้อง
header = [
    'Order ID',
    'วันที่-เวลา', 
    'ชื่อสินค้า',
    'จำนวน',
    'ราคาต่อหน่วย',
    'ราคารวม',
    'คำขอพิเศษ',
    'หมายเหตุ',
    'สถานะ'
]

# ดึงข้อมูลทั้งหมดจากฐานข้อมูล
cursor.execute('''
    SELECT o.order_id, o.created_at as order_date, mi.name, oi.quantity, 
           oi.unit_price, oi.total_price, oi.customer_request, oi.status
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN menu_items mi ON oi.item_id = mi.item_id
    WHERE o.status = 'completed'
    ORDER BY o.order_id, oi.created_at
''')

all_items = cursor.fetchall()
print(f"📊 พบข้อมูลทั้งหมด: {len(all_items)} รายการ")

# จัดรูปแบบข้อมูลใหม่
formatted_data = [header]

for item in all_items:
    order_id = str(item[0])
    order_date = datetime.strptime(item[1], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
    item_name = item[2]
    quantity = str(item[3])
    unit_price = str(int(item[4]))  # ราคาต่อหน่วย
    total_price = str(int(item[5]))  # ราคารวม
    customer_request = item[6] or ''  # คำขอพิเศษ
    notes = customer_request  # หมายเหตุ (ใช้เหมือนกับคำขอพิเศษ)
    status = 'เสร็จสิ้น' if item[7] == 'completed' else item[7]
    
    new_row = [
        order_id,
        order_date, 
        item_name,
        quantity,
        unit_price,
        total_price,
        customer_request,
        notes,
        status
    ]
    
    formatted_data.append(new_row)

# ล้างข้อมูลเก่าและใส่ข้อมูลใหม่
print("🗑️ ล้างข้อมูลเก่า...")
sheet.clear()

print("📝 เขียนข้อมูลใหม่...")
if formatted_data:
    sheet.update(range_name='A1', values=formatted_data)

# จัดรูปแบบ header
print("🎨 จัดรูปแบบ header...")
try:
    # ทำให้ header เป็นตัวหนา
    sheet.format('A1:I1', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
        'horizontalAlignment': 'CENTER'
    })
    
    # จัดความกว้างคอลัมน์
    sheet.format('A:A', {'columnWidth': 80})   # Order ID
    sheet.format('B:B', {'columnWidth': 150})  # วันที่-เวลา
    sheet.format('C:C', {'columnWidth': 200})  # ชื่อสินค้า
    sheet.format('D:D', {'columnWidth': 80})   # จำนวน
    sheet.format('E:E', {'columnWidth': 100})  # ราคาต่อหน่วย
    sheet.format('F:F', {'columnWidth': 100})  # ราคารวม
    sheet.format('G:G', {'columnWidth': 150})  # คำขอพิเศษ
    sheet.format('H:H', {'columnWidth': 150})  # หมายเหตุ
    sheet.format('I:I', {'columnWidth': 100})  # สถานะ
    
    print("✅ จัดรูปแบบเสร็จสิ้น")
except Exception as e:
    print(f"⚠️ ไม่สามารถจัดรูปแบบได้: {e}")

# สรุปผลลัพธ์
print(f"\n📋 สรุปผลลัพธ์:")
print(f"   📊 ข้อมูลทั้งหมด: {len(formatted_data)-1} รายการ (ไม่รวม header)")

# นับจำนวนรายการแต่ละ Order
order_counts = {}
for item in all_items:
    order_id = item[0]
    order_counts[order_id] = order_counts.get(order_id, 0) + 1

print(f"   📦 จำนวน Order: {len(order_counts)} orders")
for order_id, count in sorted(order_counts.items()):
    total = sum(item[5] for item in all_items if item[0] == order_id)
    print(f"      Order {order_id}: {count} รายการ, รวม {int(total)} บาท")

conn.close()
print("\n✅ แก้ไขรูปแบบ Google Sheets เสร็จสิ้น!")