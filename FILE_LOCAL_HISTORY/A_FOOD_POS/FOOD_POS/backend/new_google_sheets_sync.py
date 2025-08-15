#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ฟังก์ชันใหม่สำหรับ sync ข้อมูลไปยัง Google Sheets
ตามรูปแบบที่ผู้ใช้กำหนด (9 คอลัมน์)
"""

import json
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


def is_order_already_synced(service, spreadsheet_id, order_id):
    """
    ตรวจสอบว่าออเดอร์นี้ถูก sync ไปยัง Google Sheets แล้วหรือยัง
    
    Args:
        service: Google Sheets API service
        spreadsheet_id: ID ของ spreadsheet
        order_id: ID ของออเดอร์ที่ต้องการตรวจสอบ
    
    Returns:
        bool: True ถ้าออเดอร์ถูก sync แล้ว, False ถ้ายังไม่ถูก sync
    """
    try:
        # ดึงข้อมูลจาก Google Sheets
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Orders!A:A'  # ดึงเฉพาะคอลัมน์ Order ID
        ).execute()
        
        values = result.get('values', [])
        
        # ตรวจสอบว่ามี Order ID นี้อยู่แล้วหรือไม่
        for row in values[1:]:  # ข้าม header
            if len(row) > 0 and str(row[0]) == str(order_id):
                return True
        
        return False
        
    except Exception as e:
        print(f"[Google Sheets] Error checking if order {order_id} is synced: {e}")
        return False  # ถ้าเกิดข้อผิดพลาด ให้ sync ต่อไป


def sync_order_to_new_format(order_data, order_items=None):
    """
    ฟังก์ชันใหม่สำหรับบันทึกออเดอร์ลง Google Sheets ตามรูปแบบที่ผู้ใช้กำหนด
    
    Args:
        order_data (Dict): ข้อมูลออเดอร์
        order_items (List[Dict], optional): รายการอาหารในออเดอร์
    """
    try:
        # โหลดการตั้งค่า
        with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if not config.get('enabled', False):
            return False
        
        # เชื่อมต่อ Google Sheets
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        
        spreadsheet_id = config['spreadsheet_id']
        
        # ตรวจสอบว่าออเดอร์นี้ถูก sync ไปแล้วหรือยัง
        order_id = order_data.get('order_id')
        # ลบเงื่อนไขการตรวจสอบสถานะ
        # if is_order_already_synced(service, spreadsheet_id, order_id):
        #     print(f"[Google Sheets] Order {order_id} already synced, skipping...")
        #     return True
        
        # เตรียมข้อมูลสำหรับแต่ละรายการอาหาร
        if order_items:
            rows_to_add = []
            
            for item in order_items:
                # คำนวณราคาต่อหน่วย
                quantity = item.get('quantity', 1)
                total_price = item.get('total_price', 0)
                unit_price = total_price / quantity if quantity > 0 else 0
                
                # จัดรูปแบบวันที่
                created_at = order_data.get('created_at', '')
                if created_at:
                    try:
                        dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        formatted_date = dt.strftime('%d/%m/%Y %H:%M:%S')
                    except:
                        formatted_date = created_at
                else:
                    formatted_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                
                # สร้างแถวข้อมูลตามรูปแบบใหม่ (9 คอลัมน์)
                row = [
                    order_data.get('order_id', ''),           # A: Order ID
                    formatted_date,                           # B: วันที่
                    item.get('item_name', ''),               # C: ชื่อสินค้า
                    quantity,                                 # D: จำนวน
                    unit_price,                              # E: ราคาต่อหน่วย
                    total_price,                             # F: ราคารวม
                    item.get('special_options', ''),         # G: ตัวเลือกพิเศษ
                    item.get('customer_request', ''),        # H: หมายเหตุ
                    order_data.get('status', 'รอดำเนินการ')   # I: สถานะ
                ]
                
                rows_to_add.append(row)
            
            # เขียนข้อมูลลง Google Sheets
            if rows_to_add:
                # หาแถวสุดท้ายที่มีข้อมูล
                result = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range='Orders!A:I'
                ).execute()
                
                values = result.get('values', [])
                next_row = len(values) + 1
                
                # เขียนข้อมูลใหม่
                range_name = f'Orders!A{next_row}:I{next_row + len(rows_to_add) - 1}'
                
                body = {
                    'values': rows_to_add
                }
                
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()
                
                print(f"[Google Sheets] เพิ่มข้อมูล {len(rows_to_add)} รายการสำเร็จ")
                
                # จัดกลุ่มและคำนวณยอดรวม
                group_and_calculate_totals(service, spreadsheet_id)
                
                return True
        
        return False
        
    except Exception as e:
        print(f"[Google Sheets] เกิดข้อผิดพลาด: {e}")
        return False

def group_and_calculate_totals(service, spreadsheet_id):
    """
    จัดกลุ่มข้อมูลตาม Order ID พร้อมใส่สีและจัดรูปแบบ
    """
    import sqlite3
    import gspread
    from google.oauth2.service_account import Credentials
    from datetime import datetime
    from collections import defaultdict
    
    try:
        # เชื่อมต่อฐานข้อมูล
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ดึงข้อมูลจากฐานข้อมูล (ทุกสถานะ ไม่เฉพาะ completed)
        cursor.execute('''
            SELECT o.order_id, o.created_at as order_date, mi.name, oi.quantity, 
                   oi.unit_price, oi.total_price, oi.customer_request, o.status,
                   oi.created_at as item_created_at
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN menu_items mi ON oi.item_id = mi.item_id
            ORDER BY o.order_id DESC, oi.created_at ASC
        ''')
        
        all_items = cursor.fetchall()
        conn.close()
        
        if not all_items:
            print("[Google Sheets] ไม่พบข้อมูลที่จะจัดกลุ่ม")
            return
        
        # จัดกลุ่มข้อมูลตาม Order ID
        orders_grouped = defaultdict(list)
        for item in all_items:
            order_id = item[0]
            orders_grouped[order_id].append(item)
        
        # สร้าง header
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
                order_status = item[7]  # สถานะจริงของ order
                
                # แปลงสถานะเป็นภาษาไทย
                status_mapping = {
                    'active': 'รอดำเนินการ',
                    'pending': 'รอดำเนินการ', 
                    'completed': 'เสร็จสิ้น',
                    'cancelled': 'ยกเลิก'
                }
                status = status_mapping.get(order_status, order_status)
                
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
                            
                            # ถ้าไม่ใช่คำขอพิเศษแกะกับความเผ็ด/หวาน และไม่ใช่ "ไม่เพิ่ม" ให้ใส่ในหมายเหตุ
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
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range='Orders!A:I'
        ).execute()
        
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Orders!A1',
            valueInputOption='USER_ENTERED',
            body={'values': formatted_data}
        ).execute()
        
        # จัดรูปแบบและใส่สี
        try:
            # เชื่อมต่อ gspread สำหรับการจัดรูปแบบ
            creds = Credentials.from_service_account_file(
                'credentials.json',
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            client = gspread.authorize(creds)
            sheet = client.open_by_key(spreadsheet_id).worksheet('Orders')
            
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
                            # จัดรูปแบบแถวสรุปยอด (สีเข้ม + ตัวหนา + กึ่งกลาง)
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
                                # จัดรูปแบบแถวข้อมูล (สีอ่อน + ไม่หนา + ชิดซ้าย)
                                sheet.format(f'A{i}:I{i}', {
                                    'textFormat': {
                                        'bold': False,
                                        'fontSize': 10
                                    },
                                    'backgroundColor': order_colors[order_id]['light'],
                                    'horizontalAlignment': 'LEFT'
                                })
                        except ValueError:
                            # ถ้าไม่สามารถแปลงเป็น int ได้ ใช้สีของ Order ปัจจุบัน
                            if current_order_id and current_order_id in order_colors:
                                # จัดรูปแบบแถวข้อมูลต่อเนื่อง (สีอ่อน + ไม่หนา + ชิดซ้าย)
                                sheet.format(f'A{i}:I{i}', {
                                    'textFormat': {
                                        'bold': False,
                                        'fontSize': 10
                                    },
                                    'backgroundColor': order_colors[current_order_id]['light'],
                                    'horizontalAlignment': 'LEFT'
                                })
            
            print(f"[Google Sheets] จัดกลุ่มและใส่สีเสร็จสิ้น")
            
        except Exception as format_error:
            print(f"[Google Sheets] เกิดข้อผิดพลาดในการจัดรูปแบบ: {format_error}")
        
        print(f"[Google Sheets] จัดกลุ่มข้อมูลเสร็จสิ้น - {len(orders_grouped)} orders")
        
    except Exception as e:
        print(f"[Google Sheets] เกิดข้อผิดพลาดในการจัดกลุ่ม: {e}")

