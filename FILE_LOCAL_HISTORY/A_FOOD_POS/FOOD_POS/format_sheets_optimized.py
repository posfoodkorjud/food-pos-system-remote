#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับจัดรูปแบบ Google Sheets แบบ optimized เพื่อลด API calls
"""

import sqlite3
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from collections import defaultdict

def format_sheets_optimized():
    """
    จัดรูปแบบ Google Sheets แบบ optimized ด้วย batch requests
    """
    try:
        # โหลดการตั้งค่า Google Sheets
        with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if not config.get('enabled', False):
            print("❌ Google Sheets ไม่ได้เปิดใช้งาน")
            return False
        
        # เชื่อมต่อ Google Sheets API
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        
        spreadsheet_id = config['spreadsheet_id']
        
        print("🔄 กำลังจัดรูปแบบ Google Sheets ตามภาพที่แนบมา...")
        
        # เชื่อมต่อฐานข้อมูล
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ดึงข้อมูลออเดอร์ทั้งหมด (ไม่กรองสถานะ)
        cursor.execute('''
            SELECT o.order_id, o.table_id, o.created_at, o.total_amount, o.status, o.completed_at,
                   mi.name, oi.quantity, oi.unit_price, oi.total_price, oi.customer_request
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN menu_items mi ON oi.item_id = mi.item_id
            ORDER BY o.order_id DESC, oi.created_at ASC
        ''')
        
        all_items = cursor.fetchall()
        conn.close()
        
        if not all_items:
            print("❌ ไม่พบข้อมูลออเดอร์")
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
        
        # เก็บข้อมูลการจัดรูปแบบ
        format_requests = []
        row_formats = {}  # เก็บข้อมูลรูปแบบของแต่ละแถว
        
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
                # --- Custom logic for columns ---
                # Extract spiciness/sweetness from customer_request if present
                extra_note = ""
                special_request = customer_request or "-"
                customer_note = "-"
                display_item_name = item_name or ""
                # Example keywords for spiciness/sweetness
                if customer_request:
                    if "เผ็ด" in customer_request:
                        extra_note = "เผ็ด"
                    if "หวาน" in customer_request:
                        extra_note = extra_note + (" " if extra_note else "") + "หวาน"
                    # If customer left a note like 'ไม่ผัก', put in หมายเหตุ
                    if "ไม่ผัก" in customer_request:
                        customer_note = "ไม่ผัก"
                    # If request is extra egg/rice, put in คำขอพิเศษ
                    if any(x in customer_request for x in ["ไข่ดาว", "ไข่เจียว", "เพิ่มข้าว"]):
                        special_request = customer_request
                # Append spiciness/sweetness to item name
                if extra_note:
                    display_item_name += f" ({extra_note.strip()})"
                # กำหนดสถานะเสร็จสิ้นสำหรับสถานะที่เป็น finished
                finished_statuses = ["completed", "finished", "เสร็จสิ้น"]
                status_display = "เสร็จสิ้น" if status in finished_statuses else "รอดำเนินการ"
                row = [
                    str(order_id),
                    formatted_date,
                    display_item_name,
                    str(quantity),
                    str(int(unit_price)) if unit_price else "",
                    str(int(item_total)) if item_total else "",
                    special_request,
                    customer_note,
                    status_display
                ]
                
                formatted_data.append(row)
                
                # เก็บข้อมูลรูปแบบสำหรับแถวข้อมูล
                row_index = len(formatted_data) - 1
                row_formats[row_index] = {
                    'type': 'data',
                    'order_id': order_id,
                    'color': order_colors[order_id]['light']
                }
                
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
            
            # เก็บข้อมูลรูปแบบสำหรับแถวสรุป
            row_index = len(formatted_data) - 1
            row_formats[row_index] = {
                'type': 'summary',
                'order_id': order_id,
                'color': order_colors[order_id]['dark']
            }
        
        # ล้างข้อมูลเก่าและเขียนข้อมูลใหม่
        print("📝 กำลังเขียนข้อมูลลง Google Sheets...")
        
        # ล้างข้อมูลเก่า
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range='Orders!A:Z'
        ).execute()
        
        # เขียนข้อมูลใหม่
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Orders!A1',
            valueInputOption='USER_ENTERED',
            body={'values': formatted_data}
        ).execute()
        
        print("🎨 กำลังจัดรูปแบบด้วย Batch Requests...")
        
        # สร้าง batch requests สำหรับการจัดรูปแบบ
        requests = []
        
        # จัดรูปแบบ Header
        requests.append({
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': 9
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
                        'textFormat': {
                            'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                            'bold': True,
                            'fontSize': 12
                        },
                        'horizontalAlignment': 'CENTER',
                        'verticalAlignment': 'MIDDLE'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'
            }
        })
        
        # จัดรูปแบบแต่ละแถวข้อมูล
        for row_index, format_info in row_formats.items():
            actual_row = row_index + 1  # +1 เพราะ Google Sheets เริ่มจาก 1
            
            if format_info['type'] == 'data':
                # แถวข้อมูลสินค้า
                requests.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': actual_row - 1,
                            'endRowIndex': actual_row,
                            'startColumnIndex': 0,
                            'endColumnIndex': 9
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': format_info['color'],
                                'textFormat': {
                                    'bold': False,
                                    'fontSize': 10
                                },
                                'horizontalAlignment': 'LEFT',
                                'verticalAlignment': 'MIDDLE'
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'
                    }
                })
                
                # จัดตำแหน่งคอลัมน์ตัวเลขให้ชิดขวา (คอลัมน์ D, E, F)
                requests.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': actual_row - 1,
                            'endRowIndex': actual_row,
                            'startColumnIndex': 3,
                            'endColumnIndex': 6
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'horizontalAlignment': 'RIGHT'
                            }
                        },
                        'fields': 'userEnteredFormat(horizontalAlignment)'
                    }
                })
                
            elif format_info['type'] == 'summary':
                # แถวสรุปยอด
                requests.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': actual_row - 1,
                            'endRowIndex': actual_row,
                            'startColumnIndex': 0,
                            'endColumnIndex': 9
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': format_info['color'],
                                'textFormat': {
                                    'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                    'bold': True,
                                    'fontSize': 11
                                },
                                'horizontalAlignment': 'CENTER',
                                'verticalAlignment': 'MIDDLE'
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'
                    }
                })
        
        # ปรับความกว้างคอลัมน์อัตโนมัติ
        requests.append({
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': 0,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 9
                }
            }
        })
        
        # ส่ง batch requests
        if requests:
            body = {'requests': requests}
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
        
        print(f"✅ จัดรูปแบบ Google Sheets เสร็จสิ้น!")
        print(f"📊 จำนวน Orders: {len(orders_grouped)}")
        print(f"📝 จำนวนรายการทั้งหมด: {len(all_items)}")
        print(f"🔗 ลิงก์: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    print("🎨 เริ่มจัดรูปแบบ Google Sheets ตามภาพที่แนบมา (Optimized)")
    print("=" * 70)
    
    success = format_sheets_optimized()
    
    if success:
        print("\n🎉 จัดรูปแบบเสร็จสิ้น! Google Sheets พร้อมใช้งานแล้ว")
    else:
        print("\n❌ เกิดข้อผิดพลาดในการจัดรูปแบบ")