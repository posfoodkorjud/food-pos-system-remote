#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับซิงค์ออเดอร์ที่ขาดหายไปยัง Google Sheets
จะซิงค์เฉพาะออเดอร์ที่มีสถานะ 'completed' เท่านั้น
"""

import sqlite3
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime
from backend.new_google_sheets_sync import sync_order_to_new_format
from backend.google_sheets import is_google_sheets_enabled

def get_missing_completed_orders():
    """หาออเดอร์ที่เสร็จสิ้นแล้วแต่ยังไม่ได้ซิงค์ไป Google Sheets"""
    try:
        # เชื่อมต่อฐานข้อมูล
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ดึงออเดอร์ที่เสร็จสิ้นแล้ว
        cursor.execute("""
            SELECT order_id, table_id, session_id, status, total_amount, 
                   created_at, completed_at, updated_at
            FROM orders 
            WHERE status = 'completed'
            ORDER BY order_id DESC
        """)
        
        completed_orders = cursor.fetchall()
        
        # เชื่อมต่อ Google Sheets
        creds = Credentials.from_service_account_file(
            'credentials.json', 
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        gc = gspread.authorize(creds)
        
        with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        sheet = gc.open_by_key(config['spreadsheet_id'])
        orders_sheet = sheet.worksheet('Orders')
        sheets_data = orders_sheet.get_all_values()[1:]  # ข้าม header
        
        # หาออเดอร์ที่ไม่ซ้ำใน Google Sheets
        sheets_orders = list(set([row[0] for row in sheets_data if row and row[0]]))
        
        # หาออเดอร์ที่ยังไม่ได้ซิงค์
        missing_orders = []
        for order in completed_orders:
            order_id = str(order[0])
            if order_id not in sheets_orders:
                missing_orders.append({
                    'order_id': order[0],
                    'table_id': order[1],
                    'session_id': order[2],
                    'status': order[3],
                    'total_amount': order[4],
                    'created_at': order[5],
                    'completed_at': order[6],
                    'updated_at': order[7]
                })
        
        conn.close()
        return missing_orders
        
    except Exception as e:
        print(f"❌ ข้อผิดพลาดในการหาออเดอร์ที่ขาดหาย: {e}")
        return []

def get_order_items(order_id):
    """ดึงรายการอาหารในออเดอร์"""
    try:
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT oi.order_item_id, oi.order_id, oi.item_id, oi.quantity,
                   oi.unit_price, oi.total_price, oi.customer_request, oi.status,
                   mi.name as item_name
            FROM order_items oi
            LEFT JOIN menu_items mi ON oi.item_id = mi.item_id
            WHERE oi.order_id = ?
        """, (order_id,))
        
        order_items = []
        for item_row in cursor.fetchall():
            order_items.append({
                'order_item_id': item_row[0],
                'order_id': item_row[1],
                'item_id': item_row[2],
                'quantity': item_row[3],
                'unit_price': item_row[4],
                'total_price': item_row[5],
                'customer_request': item_row[6],
                'status': item_row[7],
                'item_name': item_row[8]
            })
        
        conn.close()
        return order_items
        
    except Exception as e:
        print(f"❌ ข้อผิดพลาดในการดึงรายการอาหาร: {e}")
        return []

def sync_missing_orders():
    """ซิงค์ออเดอร์ที่ขาดหายไปยัง Google Sheets"""
    print("🔄 เริ่มซิงค์ออเดอร์ที่ขาดหาย")
    print("=" * 50)
    
    # ตรวจสอบว่า Google Sheets เปิดใช้งานหรือไม่
    if not is_google_sheets_enabled():
        print("❌ Google Sheets ไม่ได้เปิดใช้งาน")
        return False
    
    # หาออเดอร์ที่ขาดหาย
    missing_orders = get_missing_completed_orders()
    
    if not missing_orders:
        print("✅ ไม่มีออเดอร์ที่ขาดหาย ข้อมูลซิงค์ครบถ้วนแล้ว")
        return True
    
    print(f"📋 พบออเดอร์ที่ยังไม่ได้ซิงค์: {len(missing_orders)} รายการ")
    
    success_count = 0
    error_count = 0
    
    for i, order_data in enumerate(missing_orders, 1):
        try:
            print(f"\n🔄 กำลังซิงค์ออเดอร์ {i}/{len(missing_orders)}: Order #{order_data['order_id']}")
            
            # ดึงรายการอาหารในออเดอร์
            order_items = get_order_items(order_data['order_id'])
            
            # ซิงค์ไปยัง Google Sheets
            sync_success = sync_order_to_new_format(order_data, order_items)
            
            if sync_success:
                print(f"   ✅ ซิงค์สำเร็จ: Order #{order_data['order_id']} - {order_data['total_amount']}฿")
                success_count += 1
            else:
                print(f"   ❌ ซิงค์ไม่สำเร็จ: Order #{order_data['order_id']}")
                error_count += 1
                
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: Order #{order_data['order_id']} - {e}")
            error_count += 1
    
    print(f"\n📊 สรุปผลการซิงค์:")
    print(f"   ✅ สำเร็จ: {success_count} รายการ")
    print(f"   ❌ ไม่สำเร็จ: {error_count} รายการ")
    print(f"   📈 อัตราความสำเร็จ: {(success_count/(success_count+error_count)*100):.1f}%")
    
    if success_count > 0:
        print(f"\n💡 แนะนำ: ตรวจสอบข้อมูลใน Google Sheets เพื่อยืนยันการซิงค์")
        print(f"🔗 ลิงก์: https://docs.google.com/spreadsheets/d/1QzitACA2BDNwsjYm8OvTRQORYDk6QDG3nKoM5OFSpJc/edit")
    
    return success_count > 0

def main():
    """ฟังก์ชันหลัก"""
    try:
        sync_missing_orders()
    except KeyboardInterrupt:
        print("\n⚠️ การซิงค์ถูกยกเลิกโดยผู้ใช้")
    except Exception as e:
        print(f"❌ ข้อผิดพลาดที่ไม่คาดคิด: {e}")

if __name__ == "__main__":
    main()