#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.google_sheets import google_sheets_manager
from backend.database import DatabaseManager
import gspread
from google.oauth2.service_account import Credentials

def sync_all_orders_to_sheets():
    """ซิงค์ order ทั้งหมดไปยัง Google Sheets"""
    try:
        # ตรวจสอบว่า Google Sheets เปิดใช้งานหรือไม่
        if not google_sheets_manager.enabled:
            print("Google Sheets ไม่ได้เปิดใช้งาน")
            return
        
        # ตรวจสอบการเชื่อมต่อ
        if not google_sheets_manager.service or not google_sheets_manager.spreadsheet_id:
            print("ไม่สามารถเชื่อมต่อ Google Sheets ได้")
            return
        
        print("กำลังดึงข้อมูล order ทั้งหมดจากฐานข้อมูล...")
        
        # ดึงข้อมูลจากฐานข้อมูล
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # ดึงข้อมูล orders และ order_items ทั้งหมด
        cursor.execute("""
            SELECT o.order_id, o.table_id, o.total_amount, o.status, o.completed_at,
                   oi.item_id, mi.name as item_name, oi.quantity, oi.unit_price, 
                   oi.total_price, oi.customer_request
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN menu_items mi ON oi.item_id = mi.item_id
            WHERE o.status = 'completed'
            ORDER BY o.order_id DESC, oi.order_item_id
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        print(f"พบข้อมูล {len(results)} รายการ")
        
        # จัดกลุ่มข้อมูลตาม order_id
        orders_grouped = {}
        for row in results:
            order_id, table_id, total_amount, status, completed_at, item_id, item_name, quantity, unit_price, total_price, customer_request = row
            
            if order_id not in orders_grouped:
                orders_grouped[order_id] = {
                    'table_id': table_id,
                    'total_amount': total_amount,
                    'status': status,
                    'completed_at': completed_at,
                    'items': []
                }
            
            if item_id:  # มี item
                orders_grouped[order_id]['items'].append({
                    'item_name': item_name,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': total_price,
                    'customer_request': customer_request
                })
        
        print(f"จัดกลุ่มได้ {len(orders_grouped)} orders")
        
        # เตรียมข้อมูลสำหรับ Google Sheets
        sheet_data = []
        
        # Header
        headers = ['Order ID', 'โต๊ะ', 'รายการ', 'จำนวน', 'ราคา/หน่วย', 'ราคารวม', 'คำขอพิเศษ', 'ยอดรวมออเดอร์']
        sheet_data.append(headers)
        
        # เรียงลำดับ order_id จากมากไปน้อย
        sorted_orders = sorted(orders_grouped.keys(), reverse=True)
        
        for order_id in sorted_orders:
            order = orders_grouped[order_id]
            
            if order['items']:
                # แถวแรกของ order
                first_item = order['items'][0]
                sheet_data.append([
                    f"Order {order_id}",
                    order['table_id'],
                    first_item['item_name'],
                    first_item['quantity'],
                    first_item['unit_price'],
                    first_item['total_price'],
                    first_item['customer_request'] or '',
                    order['total_amount']
                ])
                
                # แถวที่เหลือของ order
                for item in order['items'][1:]:
                    sheet_data.append([
                        '',  # Order ID ว่าง
                        '',  # โต๊ะ ว่าง
                        item['item_name'],
                        item['quantity'],
                        item['unit_price'],
                        item['total_price'],
                        item['customer_request'] or '',
                        ''   # ยอดรวม ว่าง
                    ])
                
                # แถวสรุปยอด
                sheet_data.append([
                    f"รวม Order {order_id}",
                    f"โต๊ะ {order['table_id']}",
                    '',
                    '',
                    '',
                    '',
                    '',
                    f"{order['total_amount']:.2f} บาท"
                ])
                
                # แถวว่าง
                sheet_data.append(['', '', '', '', '', '', '', ''])
        
        print(f"เตรียมข้อมูลสำหรับ Google Sheets เสร็จ: {len(sheet_data)} แถว")
        
        # เชื่อมต่อ Google Sheets ด้วย gspread
        try:
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
            client = gspread.authorize(creds)
            
            # เปิด spreadsheet
            spreadsheet = client.open_by_key(google_sheets_manager.spreadsheet_id)
            worksheet = spreadsheet.sheet1
            
            print("กำลังล้างข้อมูลเก่า...")
            worksheet.clear()
            
            print("กำลังเขียนข้อมูลใหม่...")
            worksheet.update('A1', sheet_data)
            
            print("กำลังจัดรูปแบบ...")
            
            # จัดรูปแบบ Header
            header_format = {
                'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
                'textFormat': {
                    'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                    'bold': True,
                    'fontSize': 11
                },
                'horizontalAlignment': 'CENTER'
            }
            
            worksheet.format('A1:H1', header_format)
            
            # กำหนดสีสำหรับ orders
            colors = [
                {'red': 0.9, 'green': 0.95, 'blue': 1.0},    # ฟ้าอ่อน
                {'red': 0.95, 'green': 1.0, 'blue': 0.9},    # เขียวอ่อน
                {'red': 1.0, 'green': 0.95, 'blue': 0.9},    # ส้มอ่อน
                {'red': 0.95, 'green': 0.9, 'blue': 1.0},    # ม่วงอ่อน
                {'red': 1.0, 'green': 0.9, 'blue': 0.95},    # ชมพูอ่อน
            ]
            
            # จัดรูปแบบแต่ละ order
            current_row = 2  # เริ่มจากแถวที่ 2 (หลัง header)
            color_index = 0
            
            for order_id in sorted_orders:
                order = orders_grouped[order_id]
                order_color = colors[color_index % len(colors)]
                
                # นับจำนวนแถวของ order นี้
                order_rows = len(order['items']) + 1  # +1 สำหรับแถวสรุป
                end_row = current_row + order_rows - 1
                
                # จัดรูปแบบแถวข้อมูล
                data_format = {
                    'backgroundColor': order_color,
                    'textFormat': {
                        'bold': False,
                        'fontSize': 10
                    },
                    'horizontalAlignment': 'LEFT'
                }
                
                if order_rows > 1:
                    worksheet.format(f'A{current_row}:H{end_row-1}', data_format)
                
                # จัดรูปแบบแถวสรุป (ตัวหนา + กึ่งกลาง)
                summary_format = {
                    'backgroundColor': {
                        'red': min(1.0, order_color['red'] * 0.8),
                        'green': min(1.0, order_color['green'] * 0.8),
                        'blue': min(1.0, order_color['blue'] * 0.8)
                    },
                    'textFormat': {
                        'bold': True,
                        'fontSize': 11
                    },
                    'horizontalAlignment': 'CENTER'
                }
                
                worksheet.format(f'A{end_row}:H{end_row}', summary_format)
                
                current_row = end_row + 2  # +2 เพื่อข้ามแถวว่าง
                color_index += 1
                
                print(f"จัดรูปแบบ Order {order_id} เสร็จ")
            
            print("\n=== การซิงค์เสร็จสิ้นสมบูรณ์ ===")
            print(f"✅ ซิงค์ {len(orders_grouped)} orders ทั้งหมด")
            print(f"✅ รวม {len(sheet_data)} แถวข้อมูล")
            print(f"✅ Order ID สูงสุด: {max(sorted_orders)}")
            print(f"✅ Order ID ต่ำสุด: {min(sorted_orders)}")
            print("✅ จัดรูปแบบครบถ้วน: Header, แถวข้อมูล, แถวสรุป")
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ Google Sheets: {e}")
            
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    sync_all_orders_to_sheets()