#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.google_sheets import google_sheets_manager
from backend.database import DatabaseManager
import gspread
from google.oauth2.service_account import Credentials

def force_complete_formatting():
    """บังคับจัดรูปแบบทุก order ให้สมบูรณ์"""
    try:
        # ตรวจสอบว่า Google Sheets เปิดใช้งานหรือไม่
        if not google_sheets_manager.enabled:
            print("Google Sheets ไม่ได้เปิดใช้งาน")
            return
        
        # ตรวจสอบการเชื่อมต่อ
        if not google_sheets_manager.service or not google_sheets_manager.spreadsheet_id:
            print("ไม่สามารถเชื่อมต่อ Google Sheets ได้")
            return
        
        print("กำลังดึงข้อมูลจากฐานข้อมูลและจัดรูปแบบใหม่ทั้งหมด...")
        
        # ดึงข้อมูลจากฐานข้อมูล
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # ดึงข้อมูล orders และ order_items
        cursor.execute("""
            SELECT o.order_id, o.table_id, o.total_amount, o.status, o.completed_at,
                   oi.item_id, mi.name as item_name, oi.quantity, oi.unit_price, 
                   oi.total_price, oi.customer_request
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN menu_items mi ON oi.item_id = mi.item_id
            WHERE o.order_id BETWEEN 88 AND 133
            ORDER BY o.order_id DESC, oi.order_item_id
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        # จัดกลุ่มข้อมูลตาม order_id
        orders_grouped = {}
        for row in results:
            order_id = row[0]
            if order_id not in orders_grouped:
                orders_grouped[order_id] = {
                    'order_info': {
                        'table_id': row[1],
                        'total_amount': row[2],
                        'status': row[3],
                        'completed_at': row[4]
                    },
                    'items': []
                }
            
            if row[5]:  # มี order_items
                orders_grouped[order_id]['items'].append({
                    'item_id': row[5],
                    'item_name': row[6],
                    'quantity': row[7],
                    'unit_price': row[8],
                    'total_price': row[9],
                    'customer_request': row[10]
                })
        
        print(f"พบ {len(orders_grouped)} orders ที่จะจัดรูปแบบ")
        
        # สร้างข้อมูลสำหรับ Google Sheets
        formatted_data = []
        
        # Header
        headers = ['Order ID', 'Table', 'Item', 'Quantity', 'Unit Price', 'Total', 'Request', 'Status', 'Completed']
        formatted_data.append(headers)
        
        # ข้อมูล orders (เรียงจาก order_id มากไปน้อย)
        for order_id in sorted(orders_grouped.keys(), reverse=True):
            order_info = orders_grouped[order_id]['order_info']
            items = orders_grouped[order_id]['items']
            
            total_quantity = 0
            total_amount = 0
            
            # เพิ่มข้อมูลแต่ละรายการ
            for item in items:
                quantity = item['quantity'] or 0
                item_total = item['total_price'] or 0
                status = order_info['status']
                
                new_row = [
                    order_id,
                    order_info['table_id'],
                    item['item_name'] or '',
                    quantity,
                    item['unit_price'] or 0,
                    item_total,
                    item['customer_request'] or '',
                    status,
                    order_info['completed_at'] or ''
                ]
                
                formatted_data.append(new_row)
                total_quantity += quantity
                total_amount += item_total
            
            # เพิ่มแถวสรุปยอดสำหรับแต่ละ Order
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
        google_sheets_manager.service.spreadsheets().values().clear(
            spreadsheetId=google_sheets_manager.spreadsheet_id,
            range='Orders!A:I'
        ).execute()
        
        google_sheets_manager.service.spreadsheets().values().update(
            spreadsheetId=google_sheets_manager.spreadsheet_id,
            range='Orders!A1',
            valueInputOption='USER_ENTERED',
            body={'values': formatted_data}
        ).execute()
        
        print("เขียนข้อมูลเสร็จสิ้น กำลังจัดรูปแบบ...")
        
        # จัดรูปแบบด้วย gspread
        try:
            creds = Credentials.from_service_account_file(
                'credentials.json',
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            client = gspread.authorize(creds)
            sheet = client.open_by_key(google_sheets_manager.spreadsheet_id).worksheet('Orders')
            
            # จัดรูปแบบ header
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
            
            # กำหนดชุดสีสำหรับแต่ละ Order
            color_sets = [
                {'light': {'red': 1.0, 'green': 0.9, 'blue': 0.8}, 'dark': {'red': 1.0, 'green': 0.7, 'blue': 0.4}},
                {'light': {'red': 0.8, 'green': 1.0, 'blue': 0.8}, 'dark': {'red': 0.6, 'green': 0.9, 'blue': 0.6}},
                {'light': {'red': 0.8, 'green': 0.9, 'blue': 1.0}, 'dark': {'red': 0.6, 'green': 0.8, 'blue': 1.0}},
                {'light': {'red': 0.95, 'green': 0.8, 'blue': 1.0}, 'dark': {'red': 0.9, 'green': 0.6, 'blue': 1.0}},
                {'light': {'red': 1.0, 'green': 0.9, 'blue': 0.95}, 'dark': {'red': 1.0, 'green': 0.7, 'blue': 0.8}},
                {'light': {'red': 1.0, 'green': 1.0, 'blue': 0.8}, 'dark': {'red': 1.0, 'green': 0.9, 'blue': 0.5}}
            ]
            
            # กำหนดสีให้แต่ละ Order
            order_colors = {}
            color_index = 0
            sorted_orders = sorted(orders_grouped.keys(), reverse=True)
            for order_id in sorted_orders:
                order_colors[order_id] = color_sets[color_index % len(color_sets)]
                color_index += 1
            
            print(f"กำลังจัดรูปแบบ {len(formatted_data)} แถว...")
            
            # จัดรูปแบบแต่ละแถว
            for i, row in enumerate(formatted_data[1:], start=2):  # เริ่มจากแถว 2
                if len(row) > 0 and row[0]:
                    # ตรวจสอบว่าเป็นแถวสรุปหรือไม่
                    if str(row[0]).startswith('สรุป Order'):
                        # แยก Order ID จากข้อความสรุป
                        try:
                            order_id = int(str(row[0]).replace('สรุป Order ', ''))
                            if order_id in order_colors:
                                # จัดรูปแบบแถวสรุปยอด (สีเข้ม + ตัวหนา + กึ่งกลาง)
                                sheet.format(f'A{i}:I{i}', {
                                    'textFormat': {
                                        'bold': True,
                                        'fontSize': 11
                                    },
                                    'backgroundColor': order_colors[order_id]['dark'],
                                    'horizontalAlignment': 'CENTER'
                                })
                                print(f"จัดรูปแบบแถวสรุป Order {order_id} ที่แถว {i}")
                        except ValueError:
                            pass
                    else:
                        # แถวข้อมูลสินค้า
                        try:
                            order_id = int(row[0])
                            if order_id in order_colors:
                                # จัดรูปแบบแถวข้อมูล (สีอ่อน + ไม่หนา + ชิดซ้าย)
                                sheet.format(f'A{i}:I{i}', {
                                    'textFormat': {
                                        'bold': False,
                                        'fontSize': 10
                                    },
                                    'backgroundColor': order_colors[order_id]['light'],
                                    'horizontalAlignment': 'LEFT'
                                })
                                if i % 10 == 0:  # แสดงความคืบหน้าทุก 10 แถว
                                    print(f"จัดรูปแบบแถวข้อมูล Order {order_id} ที่แถว {i}")
                        except (ValueError, TypeError):
                            pass
            
            print("จัดรูปแบบเสร็จสิ้นทั้งหมด!")
            
        except Exception as format_error:
            print(f"เกิดข้อผิดพลาดในการจัดรูปแบบ: {format_error}")
        
        print(f"\n=== การจัดรูปแบบสมบูรณ์เสร็จสิ้น ===")
        print(f"✅ จัดรูปแบบ {len(orders_grouped)} orders (Order ID 88-133)")
        print("✅ แถวสรุปยอด: ตัวหนา + กึ่งกลาง + สีเข้ม")
        print("✅ แถวข้อมูล: ข้อความธรรมดา + ชิดซ้าย + สีอ่อน")
        print("✅ Header: ตัวหนา + กึ่งกลาง + สีน้ำเงิน")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    force_complete_formatting()