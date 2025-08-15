#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gspread
from google.oauth2.service_account import Credentials
import json
import sqlite3
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

print("🔍 ตรวจสอบปัญหาในแถวที่ 2...")

# ดึงข้อมูลทั้งหมด
data = sheet.get_all_values()
header = data[0] if data else []

print(f"Header: {header}")
print(f"แถวที่ 2 (ปัญหา): {data[1] if len(data) > 1 else 'ไม่มี'}")

# ตรวจสอบข้อมูล Order 171 ในฐานข้อมูล
conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT o.order_id, o.table_id, o.session_id, o.status, o.total_amount, 
           o.created_at, o.completed_at
    FROM orders o
    WHERE o.order_id = 171
''')

order_data = cursor.fetchone()
print(f"\n📊 ข้อมูล Order 171 ในฐานข้อมูล:")
print(f"   Order ID: {order_data[0]}")
print(f"   Table ID: {order_data[1]}")
print(f"   Session ID: {order_data[2]}")
print(f"   Status: {order_data[3]}")
print(f"   Total Amount: {order_data[4]}")
print(f"   Created At: {order_data[5]}")
print(f"   Completed At: {order_data[6]}")

# สร้างข้อมูลที่ถูกต้องสำหรับ Order 171
def format_datetime(dt_str):
    if not dt_str:
        return '', ''
    try:
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        date_part = dt.strftime('%Y-%m-%d')
        time_part = dt.strftime('%H:%M:%S')
        return date_part, time_part
    except:
        return '', ''

def calculate_duration(created_at, completed_at):
    if not created_at or not completed_at:
        return ''
    try:
        created = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
        completed = datetime.strptime(completed_at, '%Y-%m-%d %H:%M:%S')
        duration = completed - created
        minutes = int(duration.total_seconds() / 60)
        return str(minutes)
    except:
        return ''

# จัดรูปแบบข้อมูลที่ถูกต้อง
created_date, created_time = format_datetime(order_data[5])
completed_date, completed_time = format_datetime(order_data[6])
duration = calculate_duration(order_data[5], order_data[6])

correct_row = [
    str(order_data[0]),  # Order ID
    f"โต๊ะ {order_data[1]}",  # Table Number
    order_data[2] or '',  # Session ID
    'เสร็จสิ้น' if order_data[3] == 'completed' else order_data[3],  # Status
    str(order_data[4]),  # Total Amount
    'เงินสด',  # Payment Method (default)
    '2',  # Customer Count (default)
    'Dine-in',  # Order Type (default)
    created_date,  # Created Date
    created_time,  # Created Time
    completed_date,  # Completed Date
    completed_time,  # Completed Time
    duration,  # Duration
    datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Updated At
]

print(f"\n✅ ข้อมูลที่ถูกต้องสำหรับ Order 171:")
for i, (col, val) in enumerate(zip(header, correct_row)):
    print(f"   {col}: {val}")

# ลบแถวที่ 2 ที่มีปัญหาและใส่ข้อมูลที่ถูกต้อง
print(f"\n🔧 แก้ไขข้อมูลในแถวที่ 2...")

# สร้างข้อมูลใหม่โดยแทนที่แถวที่ 2
new_data = [header]  # เก็บ header
new_data.append(correct_row)  # ใส่ข้อมูลที่ถูกต้องแทนแถวที่ 2

# เก็บข้อมูลแถวอื่นๆ (ข้ามแถวที่ 2 ที่มีปัญหา)
for i in range(2, len(data)):
    new_data.append(data[i])

# อัปเดต Google Sheets
sheet.clear()
if new_data:
    sheet.update(range_name='A1', values=new_data)

print(f"\n✅ แก้ไขเสร็จสิ้น!")
print(f"📊 ข้อมูลทั้งหมด: {len(new_data)-1} แถว (ไม่รวม header)")
print(f"🔗 ตรวจสอบผลลัพธ์ที่: {config.get('spreadsheet_url', 'Google Sheets')}")

conn.close()