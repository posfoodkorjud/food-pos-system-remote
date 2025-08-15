#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับจัดรูปแบบ Google Sheets ให้ตรงตามภาพที่ผู้ใช้แนบมา
"""

import sqlite3
import json
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime
from collections import defaultdict

def format_sheets_like_image():
    """
    จัดรูปแบบ Google Sheets ให้ตรงตามภาพที่ผู้ใช้แนบมา
    """
    try:
        # โหลดการตั้งค่า Google Sheets
        with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if not config.get('enabled', False):
            print("❌ Google Sheets ไม่ได้เปิดใช้งาน")
            return False
        
        # เชื่อมต่อ Google Sheets
        creds = Credentials.from_service_account_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(config['spreadsheet_id']).worksheet('Orders')
        
        print("🔄 กำลังจัดรูปแบบ Google Sheets ตามภาพที่แนบมา...")
        
        # เชื่อมต่อฐานข้อมูล
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ดึงข้อมูลออเดอร์ที่เสร็จสิ้นแล้ว
        cursor.execute('''
            SELECT o.order_id, o.table_id, o.created_at, o.total_amount, o.status, o.completed_at,
                   mi.name, oi.quantity, oi.unit_price, oi.total_price, oi.customer_request
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN menu_items mi ON oi.item_id = mi.item_id
            WHERE o.status = 'completed'
            ORDER BY o.order_id DESC, oi.created_at ASC
        ''')
        
        all_items = cursor.fetchall()
        conn.close()
        
        if not all_items:
            print("❌ ไม่พบข้อมูลออเดอร์ที่เสร็จสิ้น")
            return False
        
        # จัดกลุ่มข้อมูลตาม Order ID
        orders_grouped = defaultdict(list)
        for item in all_items:
            order_id = item[0]
            orders_grouped[order_id].append(item)
        
        # สร้าง header ตามภาพ
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
        
        # เตรียมข้อมูลสำหรับ Google Sheets
        formatted_data = [header]
        
        # สีสำหรับแต่ละ Order (ตามภาพ)
        colors = [
            {'light': {'red': 1.0, 'green': 0.9, 'blue': 0.8}, 'dark': {'red': 1.0, 'green': 0.7, 'blue': 0.4}},  # ส้ม
            {'light': {'red': 0.8, 'green': 1.0, 'blue': 0.8}, 'dark': {'red': 0.6, 'green': 0.9, 'blue': 0.6}},  # เขียว
            {'light': {'red': 0.8, 'green': 0.9, 'blue': 1.0}, 'dark': {'red': 0.6, 'green': 0.8, 'blue': 1.0}},  # ฟ้า
            {'light': {'red': 0.95, 'green': 0.8, 'blue': 1.0}, 'dark': {'red': 0.9, 'green': 0.6, 'blue': 1.0}}, # ม่วง
            {'light': {'red': 1.0, 'green': 0.9, 'blue': 0.95}, 'dark': {'red': 1.0, 'green': 0.7, 'blue': 0.8}}, # ชมพู
            {'light': {'red': 1.0, 'green': 1.0, 'blue': 0.8}, 'dark': {'red': 1.0, 'green': 0.9, 'blue': 0.5}}   # เหลือง
        ]
        
        # กำหนดสีให้แต่ละ Order
        order_colors = {}
        color_index = 0
        sorted_orders = sorted(orders_grouped.keys(), reverse=True)
        
        for order_id in sorted_orders:
            order_colors[order_id] = colors[color_index % len(colors)]
            color_index += 1
        
        # สร้างข้อมูลสำหรับแต่ละ Order
        for order_id in sorted_orders:
            items = orders_grouped[order_id]
            total_quantity = 0
            total_amount = 0
            
            # เพิ่มข้อมูลแต่ละรายการ
            for item in items:
                order_id, table_id, created_at, order_total, status, completed_at, item_name, quantity, unit_price, item_total, customer_request = item
                
                # จัดรูปแบบวันที่
                try:
                    if completed_at:
                        dt = datetime.strptime(completed_at, '%Y-%m-%d %H:%M:%S')
                    else:
                        dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    formatted_date = dt.strftime('%d/%m/%Y %H:%M:%S')
                except:
                    formatted_date = created_at or ''
                
                # สร้างแถวข้อมูล
                row = [
                    str(order_id),
                    formatted_date,
                    item_name or '',
                    str(quantity),
                    str(int(unit_price)) if unit_price else '',
                    str(int(item_total)) if item_total else '',
                    customer_request or '-',
                    '-',  # หมายเหตุ
                    'รอดำเนินการ' if status != 'completed' else 'เสร็จสิ้น'
                ]
                
                formatted_data.append(row)
                total_quantity += quantity
                total_amount += item_total
            
            # เพิ่มแถวสรุปยอด
            summary_row = [
                f'สรุป Order {order_id}',
                '',
                f'รวม {len(items)} รายการ',
                str(total_quantity),
                '',
                str(int(total_amount)),
                '',
                '',
                ''
            ]
            formatted_data.append(summary_row)
        
        # ล้างข้อมูลเก่าและเขียนข้อมูลใหม่
        print("📝 กำลังเขียนข้อมูลลง Google Sheets...")
        sheet.clear()
        sheet.update('A1', formatted_data)
        
        # จัดรูปแบบ Header
        print("🎨 กำลังจัดรูปแบบ Header...")
        sheet.format('A1:I1', {
            'textFormat': {
                'bold': True,
                'fontSize': 12,
                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
            },
            'backgroundColor': {
                'red': 0.2, 
                'green': 0.4, 
                'blue': 0.8
            },
            'horizontalAlignment': 'CENTER',
            'verticalAlignment': 'MIDDLE'
        })
        
        # จัดรูปแบบข้อมูลแต่ละแถว
        print("🌈 กำลังใส่สีและจัดรูปแบบข้อมูล...")
        current_order_id = None
        
        for i, row in enumerate(formatted_data[1:], start=2):  # เริ่มจากแถว 2
            if len(row) > 0 and row[0]:
                # ตรวจสอบว่าเป็นแถวสรุปหรือไม่
                if row[0].startswith('สรุป Order'):
                    # แยก Order ID จากข้อความสรุป
                    try:
                        order_id = int(row[0].replace('สรุป Order ', ''))
                        if order_id in order_colors:
                            # จัดรูปแบบแถวสรุป (สีเข้ม + ตัวหนา + กึ่งกลาง)
                            sheet.format(f'A{i}:I{i}', {
                                'textFormat': {
                                    'bold': True,
                                    'fontSize': 11,
                                    'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
                                },
                                'backgroundColor': order_colors[order_id]['dark'],
                                'horizontalAlignment': 'CENTER',
                                'verticalAlignment': 'MIDDLE'
                            })
                    except ValueError:
                        pass
                else:
                    # แถวข้อมูลสินค้า
                    try:
                        order_id = int(row[0])
                        current_order_id = order_id
                        if order_id in order_colors:
                            # จัดรูปแบบแถวข้อมูล (สีอ่อน + ไม่หนา + ชิดซ้าย)
                            sheet.format(f'A{i}:I{i}', {
                                'textFormat': {
                                    'bold': False,
                                    'fontSize': 10
                                },
                                'backgroundColor': order_colors[order_id]['light'],
                                'horizontalAlignment': 'LEFT',
                                'verticalAlignment': 'MIDDLE'
                            })
                            
                            # จัดตำแหน่งคอลัมน์ตัวเลขให้ชิดขวา
                            sheet.format(f'D{i}:F{i}', {
                                'horizontalAlignment': 'RIGHT'
                            })
                    except ValueError:
                        # ถ้าไม่สามารถแปลงเป็น int ได้ ใช้สีของ Order ปัจจุบัน
                        if current_order_id and current_order_id in order_colors:
                            sheet.format(f'A{i}:I{i}', {
                                'textFormat': {
                                    'bold': False,
                                    'fontSize': 10
                                },
                                'backgroundColor': order_colors[current_order_id]['light'],
                                'horizontalAlignment': 'LEFT',
                                'verticalAlignment': 'MIDDLE'
                            })
        
        # ปรับความกว้างคอลัมน์
        print("📏 กำลังปรับความกว้างคอลัมน์...")
        sheet.columns_auto_resize(0, 8)  # ปรับคอลัมน์ A-I อัตโนมัติ
        
        print(f"✅ จัดรูปแบบ Google Sheets เสร็จสิ้น!")
        print(f"📊 จำนวน Orders: {len(orders_grouped)}")
        print(f"📝 จำนวนรายการทั้งหมด: {len(all_items)}")
        print(f"🔗 ลิงก์: https://docs.google.com/spreadsheets/d/{config['spreadsheet_id']}/edit")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    print("🎨 เริ่มจัดรูปแบบ Google Sheets ตามภาพที่แนบมา")
    print("=" * 60)
    
    success = format_sheets_like_image()
    
    if success:
        print("\n🎉 จัดรูปแบบเสร็จสิ้น! Google Sheets พร้อมใช้งานแล้ว")
    else:
        print("\n❌ เกิดข้อผิดพลาดในการจัดรูปแบบ")