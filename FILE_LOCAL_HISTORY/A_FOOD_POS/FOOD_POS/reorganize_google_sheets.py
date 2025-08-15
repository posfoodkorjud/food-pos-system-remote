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

print("🔧 กำลังจัดระเบียบ Google Sheets ใหม่...")

# สร้าง header ที่สวยงาม
header = [
    'Order ID',
    'วันที่-เวลา', 
    'ชื่อสินค้า',
    'จำนวน',
    'ราคาต่อหน่วย (บาท)',
    'ราคารวม (บาท)',
    'คำขอพิเศษ',
    'หมายเหตุ',
    'สถานะ'
]

# ดึงข้อมูลทั้งหมดจากฐานข้อมูล และเรียงลำดับอย่างชัดเจน
cursor.execute('''
    SELECT o.order_id, o.created_at as order_date, mi.name, oi.quantity, 
           oi.unit_price, oi.total_price, oi.customer_request, oi.status,
           oi.created_at as item_created_at
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN menu_items mi ON oi.item_id = mi.item_id
    WHERE o.status = 'completed'
    ORDER BY o.order_id ASC, oi.created_at ASC
''')

all_items = cursor.fetchall()
print(f"📊 พบข้อมูลทั้งหมด: {len(all_items)} รายการ")

# จัดรูปแบบข้อมูลใหม่อย่างเป็นระเบียบ
formatted_data = [header]

for item in all_items:
    order_id = str(item[0])
    # แปลงวันที่ให้เป็นรูปแบบไทย
    order_date = datetime.strptime(item[1], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
    item_name = item[2]
    quantity = str(item[3])
    unit_price = f"{int(item[4])}"
    total_price = f"{int(item[5])}"
    customer_request = item[6] or '-'
    notes = customer_request if customer_request != '-' else '-'
    status = 'เสร็จสิ้น'
    
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

# ล้างข้อมูลเก่าทั้งหมด
print("🗑️ ล้างข้อมูลเก่าทั้งหมด...")
sheet.clear()

# เขียนข้อมูลใหม่
print("📝 เขียนข้อมูลใหม่อย่างเป็นระเบียบ...")
if formatted_data:
    sheet.update(range_name='A1', values=formatted_data)

# จัดรูปแบบให้สวยงาม
print("🎨 จัดรูปแบบให้สวยงาม...")
try:
    # ทำให้ header เป็นตัวหนาและมีสีพื้นหลัง
    sheet.format('A1:I1', {
        'textFormat': {
            'bold': True,
            'fontSize': 12
        },
        'backgroundColor': {
            'red': 0.2, 
            'green': 0.6, 
            'blue': 0.9
        },
        'horizontalAlignment': 'CENTER',
        'verticalAlignment': 'MIDDLE'
    })
    
    # จัดความกว้างคอลัมน์ให้เหมาะสม
    sheet.format('A:A', {'columnWidth': 100})   # Order ID
    sheet.format('B:B', {'columnWidth': 160})   # วันที่-เวลา
    sheet.format('C:C', {'columnWidth': 220})   # ชื่อสินค้า
    sheet.format('D:D', {'columnWidth': 80})    # จำนวน
    sheet.format('E:E', {'columnWidth': 120})   # ราคาต่อหน่วย
    sheet.format('F:F', {'columnWidth': 120})   # ราคารวม
    sheet.format('G:G', {'columnWidth': 180})   # คำขอพิเศษ
    sheet.format('H:H', {'columnWidth': 180})   # หมายเหตุ
    sheet.format('I:I', {'columnWidth': 100})   # สถานะ
    
    # จัดตำแหน่งข้อความ
    if len(formatted_data) > 1:
        data_range = f'A2:I{len(formatted_data)}'
        sheet.format(data_range, {
            'horizontalAlignment': 'LEFT',
            'verticalAlignment': 'MIDDLE'
        })
        
        # จัดตำแหน่งตัวเลขให้อยู่ตรงกลาง
        sheet.format(f'D2:F{len(formatted_data)}', {
            'horizontalAlignment': 'CENTER'
        })
    
    # เพิ่มเส้นขอบ
    if len(formatted_data) > 1:
        sheet.format(f'A1:I{len(formatted_data)}', {
            'borders': {
                'top': {'style': 'SOLID'},
                'bottom': {'style': 'SOLID'},
                'left': {'style': 'SOLID'},
                'right': {'style': 'SOLID'}
            }
        })
    
    print("✅ จัดรูปแบบเสร็จสิ้น")
except Exception as e:
    print(f"⚠️ ไม่สามารถจัดรูปแบบได้: {e}")

# สรุปผลลัพธ์อย่างละเอียด
print(f"\n📋 สรุปผลลัพธ์:")
print(f"   📊 ข้อมูลทั้งหมด: {len(formatted_data)-1} รายการ")

# นับจำนวนรายการและยอดรวมแต่ละ Order
order_summary = {}
for item in all_items:
    order_id = item[0]
    if order_id not in order_summary:
        order_summary[order_id] = {'count': 0, 'total': 0}
    order_summary[order_id]['count'] += 1
    order_summary[order_id]['total'] += item[5]

print(f"   📦 จำนวน Orders: {len(order_summary)} orders")
print(f"\n📊 รายละเอียดแต่ละ Order:")
for order_id in sorted(order_summary.keys()):
    count = order_summary[order_id]['count']
    total = int(order_summary[order_id]['total'])
    print(f"   Order {order_id}: {count} รายการ, รวม {total:,} บาท")

# ตรวจสอบ Order 170 โดยเฉพาะ
order_170_items = [item for item in all_items if item[0] == 170]
if order_170_items:
    print(f"\n🎯 Order 170 มีรายการดังนี้:")
    for i, item in enumerate(order_170_items, 1):
        print(f"   {i}. {item[2]} - จำนวน: {item[3]}, ราคา: {int(item[5])} บาท")
    
    # ตรวจสอบว่ามี "น้ำเงาะ+เนื้อเงาะ" หรือไม่
    has_rambutan = any('น้ำเงาะ+เนื้อเงาะ' in item[2] for item in order_170_items)
    print(f"   ✅ มี 'น้ำเงาะ+เนื้อเงาะ': {'ใช่' if has_rambutan else 'ไม่'}")

conn.close()
print(f"\n✅ จัดระเบียบ Google Sheets เสร็จสิ้นแล้ว!")
print(f"📱 ข้อมูลถูกเรียงลำดับตาม Order ID และเวลาที่สั่งอย่างเป็นระเบียบ")