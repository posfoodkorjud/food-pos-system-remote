#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime
from collections import defaultdict

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

print("🔧 กำลังจัดกลุ่มข้อมูลตาม Order ID พร้อมสรุปยอด...")

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

# ดึงข้อมูลทั้งหมดจากฐานข้อมูล และเรียงลำดับตาม Order ID (ใหม่ไปเก่า) แล้วตามเวลา
cursor.execute('''
    SELECT o.order_id, o.created_at as order_date, mi.name, oi.quantity, 
           oi.unit_price, oi.total_price, oi.customer_request, oi.status,
           oi.created_at as item_created_at
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN menu_items mi ON oi.item_id = mi.item_id
    WHERE o.status = 'completed'
    ORDER BY o.order_id DESC, oi.created_at ASC
''')

all_items = cursor.fetchall()
print(f"📊 พบข้อมูลทั้งหมด: {len(all_items)} รายการ")

# จัดกลุ่มข้อมูลตาม Order ID
orders_grouped = defaultdict(list)
for item in all_items:
    order_id = item[0]
    orders_grouped[order_id].append(item)

# สร้างข้อมูลที่จัดรูปแบบแล้ว
formatted_data = [header]

# เรียงลำดับ Order ID จากใหม่ไปเก่า
for order_id in sorted(orders_grouped.keys(), reverse=True):
    items = orders_grouped[order_id]
    
    # เพิ่มรายการสินค้าในแต่ละ Order
    total_quantity = 0
    total_amount = 0
    
    for item in items:
        order_date = datetime.strptime(item[1], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
        item_name = item[2]
        quantity = item[3]
        unit_price = int(item[4])
        item_total = int(item[5])
        customer_request = item[6] or ''
        status = 'เสร็จสิ้น'
        
        # แยกข้อมูลจาก customer_request
        special_request_text = '-'
        notes_text = '-'
        spice_level = None
        
        if customer_request and customer_request.strip():
            # แยกข้อมูลตาม | ก่อน
            parts = customer_request.split('|')
            
            # ตรวจหาระดับความเผ็ด/หวาน
            spice_patterns = ['หวานปกติ', 'หวานน้อย', 'หวานมาก', 'เผ็ดน้อย', 'เผ็ดปานกลาง', 'เผ็ดมาก', 'เผ็ดพิเศษ', 'ไม่เผ็ด', 'ปกติ']
            special_requests = []
            other_notes = []
            
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                    
                # ตรวจสอบระดับความเผ็ด/หวาน
                is_spice = False
                for pattern in spice_patterns:
                    if part == pattern or pattern in part:
                        if not spice_level:  # เก็บระดับความเผ็ด/หวานแรกที่เจอ
                            spice_level = pattern
                        is_spice = True
                        break
                
                if is_spice:
                    continue
                    
                # ตรวจหาคำขอพิเศษ (ไข่เจียว, ไข่ดาว, เพิ่มข้าว)
                special_keywords = ['ไข่เจียว', 'ไข่ดาว', 'เพิ่มข้าว', 'เพิ่ม ข้าว']
                
                # แยกคำขอพิเศษและหมายเหตุในแต่ละส่วน
                sub_parts = part.split(',')
                for sub_part in sub_parts:
                    sub_part = sub_part.strip()
                    if not sub_part:
                        continue
                        
                    is_special = False
                    for keyword in special_keywords:
                        if keyword in sub_part:
                            special_requests.append(sub_part)
                            is_special = True
                            break
                    
                    # ถ้าไม่ใช่คำขอพิเศษและไม่ใช่ระดับความเผ็ด/หวาน และไม่ใช่ "ไม่เพิ่ม" ให้ใส่ในหมายเหตุ
                    if not is_special and sub_part not in ['ไม่เพิ่ม', 'ปกติ'] and not any(spice in sub_part for spice in spice_patterns):
                        other_notes.append(sub_part)
            
            special_request_text = ', '.join(special_requests) if special_requests else '-'
            notes_text = ', '.join(other_notes) if other_notes else '-'
        
        # เพิ่มระดับความเผ็ดในวงเล็บหลังชื่อสินค้า
        if spice_level:
            item_name = f"{item_name} ({spice_level})"
        
        new_row = [
            str(order_id),
            order_date, 
            item_name,
            str(quantity),
            str(unit_price),
            str(item_total),
            special_request_text,
            notes_text,
            status
        ]
        
        formatted_data.append(new_row)
        total_quantity += quantity
        total_amount += item_total
    
    # เพิ่มแถวสรุปยอดสำหรับแต่ละ Order
    summary_row = [
        f"สรุป Order {order_id}",
        "",
        f"รวม {len(items)} รายการ",
        str(total_quantity),
        "",
        f"{total_amount:,}",
        "",
        "",
        "สรุปยอด"
    ]
    formatted_data.append(summary_row)
    
    # เพิ่มแถวว่างเพื่อแยกแต่ละ Order
    empty_row = ["", "", "", "", "", "", "", "", ""]
    formatted_data.append(empty_row)

# ลบแถวว่างสุดท้าย
if formatted_data and all(cell == "" for cell in formatted_data[-1]):
    formatted_data.pop()

# ล้างข้อมูลเก่าทั้งหมด
print("🗑️ ล้างข้อมูลเก่าทั้งหมด...")
sheet.clear()

# เขียนข้อมูลใหม่
print("📝 เขียนข้อมูลที่จัดกลุ่มแล้ว...")
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
    
    # จัดความกว้างคอลัมน์ให้เหมาะสม (ใช้ batch_update แทน)
    requests = []
    column_widths = [
        ('A', 120),   # Order ID
        ('B', 160),   # วันที่-เวลา
        ('C', 250),   # ชื่อสินค้า
        ('D', 80),    # จำนวน
        ('E', 120),   # ราคาต่อหน่วย
        ('F', 120),   # ราคารวม
        ('G', 180),   # คำขอพิเศษ
        ('H', 180),   # หมายเหตุ
        ('I', 100)    # สถานะ
    ]
    
    for col, width in column_widths:
        col_index = ord(col) - ord('A')
        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet.id,
                    'dimension': 'COLUMNS',
                    'startIndex': col_index,
                    'endIndex': col_index + 1
                },
                'properties': {
                    'pixelSize': width
                },
                'fields': 'pixelSize'
            }
        })
    
    if requests:
        sheet.spreadsheet.batch_update({'requests': requests})
    
    # กำหนดชุดสีสำหรับแต่ละ Order (สีอ่อนและสีเข้ม)
    color_sets = [
        # ชุดสีส้ม
        {
            'light': {'red': 1.0, 'green': 0.9, 'blue': 0.8},    # ส้มอ่อน
            'dark': {'red': 1.0, 'green': 0.7, 'blue': 0.4}      # ส้มเข้ม
        },
        # ชุดสีเขียว
        {
            'light': {'red': 0.8, 'green': 1.0, 'blue': 0.8},    # เขียวอ่อน
            'dark': {'red': 0.6, 'green': 0.9, 'blue': 0.6}      # เขียวเข้ม
        },
        # ชุดสีฟ้า
        {
            'light': {'red': 0.8, 'green': 0.9, 'blue': 1.0},    # ฟ้าอ่อน
            'dark': {'red': 0.6, 'green': 0.8, 'blue': 1.0}      # ฟ้าเข้ม
        },
        # ชุดสีม่วง
        {
            'light': {'red': 0.95, 'green': 0.8, 'blue': 1.0},   # ม่วงอ่อน
            'dark': {'red': 0.9, 'green': 0.6, 'blue': 1.0}      # ม่วงเข้ม
        },
        # ชุดสีชมพู
        {
            'light': {'red': 1.0, 'green': 0.9, 'blue': 0.95},   # ชมพูอ่อน
            'dark': {'red': 1.0, 'green': 0.7, 'blue': 0.8}      # ชมพูเข้ม
        },
        # ชุดสีเหลือง
        {
            'light': {'red': 1.0, 'green': 1.0, 'blue': 0.8},    # เหลืองอ่อน
            'dark': {'red': 1.0, 'green': 0.9, 'blue': 0.5}      # เหลืองเข้ม
        }
    ]
    
    # ติดตามสีที่ใช้สำหรับแต่ละ Order
    order_colors = {}
    color_index = 0
    
    # กำหนดสีให้แต่ละ Order (เรียงตาม Order ID จากมากไปน้อย)
    sorted_orders = sorted(orders_grouped.keys(), reverse=True)
    for order_id in sorted_orders:
        order_colors[order_id] = color_sets[color_index % len(color_sets)]
        color_index += 1
    
    # จัดรูปแบบสีสำหรับแต่ละแถว
    current_order_id = None
    for i, row in enumerate(formatted_data[1:], start=2):  # เริ่มจากแถว 2 (ข้าม header)
        if len(row) > 0:
            # ตรวจสอบว่าเป็นแถวสรุปหรือไม่
            if row[0].startswith('สรุป Order'):
                # แยก Order ID จากข้อความสรุป
                order_id = int(row[0].replace('สรุป Order ', ''))
                if order_id in order_colors:
                    # จัดรูปแบบแถวสรุปยอด (สีเข้ม)
                    sheet.format(f'A{i}:I{i}', {
                        'textFormat': {
                            'bold': True,
                            'fontSize': 11
                        },
                        'backgroundColor': order_colors[order_id]['dark'],
                        'horizontalAlignment': 'CENTER'
                    })
            elif row[0] and row[0] != "":
                # แถวข้อมูลสินค้า - ดึง Order ID จากคอลัมน์แรก
                try:
                    order_id = int(row[0])
                    current_order_id = order_id
                    if order_id in order_colors:
                        # จัดรูปแบบแถวข้อมูล (สีอ่อน)
                        sheet.format(f'A{i}:I{i}', {
                            'backgroundColor': order_colors[order_id]['light']
                        })
                except ValueError:
                    # ถ้าไม่สามารถแปลงเป็น int ได้ ใช้สีของ Order ปัจจุบัน
                    if current_order_id and current_order_id in order_colors:
                        sheet.format(f'A{i}:I{i}', {
                            'backgroundColor': order_colors[current_order_id]['light']
                        })
    
    # จัดตำแหน่งข้อความสำหรับข้อมูลทั่วไป
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
print(f"   📊 ข้อมูลทั้งหมด: {len(all_items)} รายการ")
print(f"   📦 จำนวน Orders: {len(orders_grouped)} orders")

# แสดงรายละเอียดแต่ละ Order (เรียงจากใหม่ไปเก่า)
print(f"\n📊 รายละเอียดแต่ละ Order (เรียงจากใหม่ไปเก่า):")
for order_id in sorted(orders_grouped.keys(), reverse=True):
    items = orders_grouped[order_id]
    total_amount = sum(item[5] for item in items)
    total_quantity = sum(item[3] for item in items)
    print(f"   Order {order_id}: {len(items)} รายการ, จำนวนรวม {total_quantity} ชิ้น, ยอดรวม {int(total_amount):,} บาท")

# ตรวจสอบ Order 170 โดยเฉพาะ
if 170 in orders_grouped:
    order_170_items = orders_grouped[170]
    print(f"\n🎯 Order 170 มีรายการดังนี้:")
    for i, item in enumerate(order_170_items, 1):
        print(f"   {i}. {item[2]} - จำนวน: {item[3]}, ราคา: {int(item[5])} บาท")
    
    # ตรวจสอบว่ามี "น้ำเงาะ+เนื้อเงาะ" หรือไม่
    has_rambutan = any('น้ำเงาะ+เนื้อเงาะ' in item[2] for item in order_170_items)
    print(f"   ✅ มี 'น้ำเงาะ+เนื้อเงาะ': {'ใช่' if has_rambutan else 'ไม่'}")

conn.close()
print(f"\n✅ จัดกลุ่มข้อมูลตาม Order ID พร้อมสรุปยอดเสร็จสิ้นแล้ว!")
print(f"📱 ข้อมูลถูกจัดกลุ่มตาม Order ID (ใหม่ไปเก่า) พร้อมสรุปยอดใต้แต่ละกลุ่ม")