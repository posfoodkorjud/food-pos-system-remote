#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับปรับปรุงรูปแบบข้อมูลใน Google Sheets ให้ตรงกับตัวอย่าง
"""

import gspread
from google.oauth2.service_account import Credentials
import json
import sqlite3
from datetime import datetime
import pandas as pd

def load_config():
    """โหลดการตั้งค่า Google Sheets"""
    try:
        with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ ไม่พบไฟล์ google_sheets_config.json")
        return None

def connect_to_sheets():
    """เชื่อมต่อกับ Google Sheets"""
    config = load_config()
    if not config:
        return None, None
    
    try:
        # ตั้งค่า credentials
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(
            'credentials.json', 
            scopes=scope
        )
        
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(config['spreadsheet_id'])
        
        return client, spreadsheet
    except Exception as e:
        print(f"❌ เชื่อมต่อ Google Sheets ไม่สำเร็จ: {e}")
        return None, None

def get_database_orders():
    """ดึงข้อมูลออเดอร์จากฐานข้อมูล"""
    try:
        conn = sqlite3.connect('pos_database.db')
        
        # ดึงข้อมูลออเดอร์ที่เสร็จสิ้นแล้ว
        query = """
        SELECT
            o.order_id,
            o.created_at,
            mi.name as item_name,
            oi.quantity,
            oi.unit_price,
            oi.total_price,
            oi.customer_request,
            '' as notes,
            o.status
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN menu_items mi ON oi.item_id = mi.item_id
        WHERE o.status = 'completed'
        ORDER BY o.created_at DESC, o.order_id DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    except Exception as e:
        print(f"❌ ดึงข้อมูลจากฐานข้อมูลไม่สำเร็จ: {e}")
        return None

def format_datetime(dt_str):
    """แปลงรูปแบบวันที่เวลา"""
    try:
        # แปลงจาก ISO format เป็น DD/MM/YYYY HH:MM:SS
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    except:
        return dt_str

def format_status(status):
    """แปลงสถานะเป็นภาษาไทย"""
    status_map = {
        'completed': 'เสร็จสิ้น',
        'active': 'กำลังทำ',
        'pending': 'รอดำเนินการ',
        'cancelled': 'ยกเลิก',
        'rejected': 'ปฏิเสธ'
    }
    return status_map.get(status, status)

def update_sheets_format():
    """ปรับปรุงรูปแบบข้อมูลใน Google Sheets"""
    print("🔄 เริ่มปรับปรุงรูปแบบข้อมูลใน Google Sheets...")
    
    # เชื่อมต่อ Google Sheets
    client, spreadsheet = connect_to_sheets()
    if not client or not spreadsheet:
        return False
    
    # ดึงข้อมูลจากฐานข้อมูล
    df = get_database_orders()
    if df is None or df.empty:
        print("❌ ไม่มีข้อมูลออเดอร์ในฐานข้อมูล")
        return False
    
    try:
        # เข้าถึงชีท Orders
        orders_sheet = spreadsheet.worksheet('Orders')
        
        # ล้างข้อมูลเก่า (เก็บเฉพาะ header)
        orders_sheet.clear()
        
        # ตั้งค่า header ตามตัวอย่าง
        headers = [
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
        
        # เพิ่ม header
        orders_sheet.append_row(headers)
        
        # เตรียมข้อมูลสำหรับอัพเดท
        rows_to_add = []
        
        for _, row in df.iterrows():
            formatted_row = [
                str(row['order_id']),
                format_datetime(row['created_at']),
                str(row['item_name']) if pd.notna(row['item_name']) else '',
                int(row['quantity']) if pd.notna(row['quantity']) else 0,
                float(row['unit_price']) if pd.notna(row['unit_price']) else 0.0,
                float(row['total_price']) if pd.notna(row['total_price']) else 0.0,
                str(row['customer_request']) if pd.notna(row['customer_request']) else '-',
                str(row['notes']) if pd.notna(row['notes']) else '-',
                format_status(row['status'])
            ]
            rows_to_add.append(formatted_row)
        
        # อัพเดทข้อมูลทีละ batch เพื่อประสิทธิภาพ
        batch_size = 100
        for i in range(0, len(rows_to_add), batch_size):
            batch = rows_to_add[i:i + batch_size]
            orders_sheet.append_rows(batch)
            print(f"📝 อัพเดทข้อมูล {i + len(batch)}/{len(rows_to_add)} แถว")
        
        print(f"✅ ปรับปรุงข้อมูลสำเร็จ! อัพเดท {len(rows_to_add)} แถว")
        print(f"🔗 ดูผลลัพธ์ที่: https://docs.google.com/spreadsheets/d/{spreadsheet.id}/edit")
        
        return True
        
    except Exception as e:
        print(f"❌ ปรับปรุงข้อมูลไม่สำเร็จ: {e}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("=" * 60)
    print("🔧 สคริปต์ปรับปรุงรูปแบบข้อมูล Google Sheets")
    print("=" * 60)
    
    # ตรวจสอบการเชื่อมต่อ
    client, spreadsheet = connect_to_sheets()
    if not client:
        return
    
    print(f"📊 เชื่อมต่อกับ: {spreadsheet.title}")
    print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}/edit")
    
    # ยืนยันการดำเนินการ
    confirm = input("\n⚠️  การดำเนินการนี้จะลบข้อมูลเก่าและอัพเดทใหม่ ต้องการดำเนินการต่อหรือไม่? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ ยกเลิกการดำเนินการ")
        return
    
    # ปรับปรุงข้อมูล
    success = update_sheets_format()
    
    if success:
        print("\n🎉 ปรับปรุงข้อมูลเสร็จสิ้น!")
        print("📋 รูปแบบข้อมูลตรงกับตัวอย่างที่แนบมาแล้ว")
    else:
        print("\n❌ เกิดข้อผิดพลาดในการปรับปรุงข้อมูล")

if __name__ == "__main__":
    main()