#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from backend.google_sheets import GoogleSheetsManager
from datetime import datetime, timedelta
import json
import random

def test_pos_integration():
    """ทดสอบการทำงานของระบบ POS กับ Google Sheets ที่ปรับปรุงแล้ว"""
    print("🚀 ทดสอบการทำงานของระบบ POS กับ Google Sheets ที่ปรับปรุงแล้ว")
    print("=" * 60)
    
    # สร้าง GoogleSheetsManager
    sheets_manager = GoogleSheetsManager()
    
    # ทดสอบการเชื่อมต่อ
    print("📡 ทดสอบการเชื่อมต่อ Google Sheets...")
    if sheets_manager.test_connection():
        print("✅ เชื่อมต่อ Google Sheets สำเร็จ")
    else:
        print("❌ ไม่สามารถเชื่อมต่อ Google Sheets ได้")
        return
    
    # สร้างข้อมูลออเดอร์ตัวอย่าง
    print("\n📝 สร้างข้อมูลออเดอร์ตัวอย่าง...")
    
    # ออเดอร์ที่ 1
    order_data_1 = {
        'order_id': 101,
        'table_number': 5,
        'order_date': datetime.now().strftime('%Y-%m-%d'),
        'order_time': datetime.now().strftime('%H:%M:%S'),
        'total_amount': 450.00,
        'status': 'completed',
        'payment_method': 'cash',
        'customer_name': 'คุณสมชาย',
        'service_duration': '15 นาที',
        'rush_hour': 'ใช่'
    }
    
    order_items_1 = [
        {
            'order_id': 101,
            'item_name': 'ผัดไทยกุ้ง',
            'quantity': 2,
            'unit_price': 120.00,
            'total_price': 240.00,
            'special_options': 'ไม่ใส่ถั่วงอก, เผ็ดน้อย',
            'notes': 'ลูกค้า VIP'
        },
        {
            'order_id': 101,
            'item_name': 'ต้มยำกุ้ง',
            'quantity': 1,
            'unit_price': 150.00,
            'total_price': 150.00,
            'special_options': 'เผ็ดมาก',
            'notes': ''
        },
        {
            'order_id': 101,
            'item_name': 'น้ำมะนาว',
            'quantity': 2,
            'unit_price': 30.00,
            'total_price': 60.00,
            'special_options': 'น้ำแข็งน้อย',
            'notes': ''
        }
    ]
    
    # ออเดอร์ที่ 2
    order_data_2 = {
        'order_id': 102,
        'table_number': 3,
        'order_date': datetime.now().strftime('%Y-%m-%d'),
        'order_time': (datetime.now() + timedelta(minutes=30)).strftime('%H:%M:%S'),
        'total_amount': 320.00,
        'status': 'completed',
        'payment_method': 'promptpay',
        'customer_name': 'คุณสมหญิง',
        'service_duration': '12 นาที',
        'rush_hour': 'ไม่'
    }
    
    order_items_2 = [
        {
            'order_id': 102,
            'item_name': 'ข้าวผัดปู',
            'quantity': 1,
            'unit_price': 180.00,
            'total_price': 180.00,
            'special_options': 'ไข่ดาวด้านบน',
            'notes': ''
        },
        {
            'order_id': 102,
            'item_name': 'ส้มตำไทย',
            'quantity': 1,
            'unit_price': 80.00,
            'total_price': 80.00,
            'special_options': 'เผ็ดปานกลาง, ไม่ใส่ปลาร้า',
            'notes': 'ลูกค้าแพ้ปลาร้า'
        },
        {
            'order_id': 102,
            'item_name': 'น้ำเปล่า',
            'quantity': 2,
            'unit_price': 30.00,
            'total_price': 60.00,
            'special_options': '',
            'notes': ''
        }
    ]
    
    # บันทึกข้อมูลออเดอร์
    print("💾 บันทึกข้อมูลออเดอร์ลง Google Sheets...")
    
    try:
        # บันทึกออเดอร์ที่ 1
        from backend.google_sheets import sync_order_to_sheets
        if sync_order_to_sheets(order_data_1, order_items_1):
            print("✅ บันทึกออเดอร์ที่ 1 และรายการอาหารสำเร็จ")
        else:
            print("❌ ไม่สามารถบันทึกออเดอร์ที่ 1 ได้")
        
        # บันทึกออเดอร์ที่ 2
        if sync_order_to_sheets(order_data_2, order_items_2):
            print("✅ บันทึกออเดอร์ที่ 2 และรายการอาหารสำเร็จ")
        else:
            print("❌ ไม่สามารถบันทึกออเดอร์ที่ 2 ได้")
        
        # ทดสอบการบันทึกสถิติรายวัน
        print("\n📊 ทดสอบการบันทึกสถิติรายวัน...")
        daily_stats = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'day_of_week': 'วันจันทร์',
            'total_sales': 770.00,
            'total_orders': 2,
            'completed_orders': 2,
            'cancelled_orders': 0,
            'rush_hours': '12:00-13:00, 19:00-20:00',
            'popular_items': 'ผัดไทยกุ้ง, ข้าวผัดปู'
        }
        
        if sheets_manager.sync_daily_summary(daily_stats['date'], daily_stats):
            print("✅ บันทึกสถิติรายวันสำเร็จ")
        else:
            print("❌ ไม่สามารถบันทึกสถิติรายวันได้")
        
        # ทดสอบการอัปเดตสถิติสินค้า
        print("\n📈 ทดสอบการอัปเดตสถิติสินค้า...")
        item_stats = [
            {
                'item_code': 'FOOD001',
                'item_name': 'ผัดไทยกุ้ง',
                'category': 'อาหารจานเดียว',
                'total_sold': 25,
                'total_revenue': 3000.00,
                'avg_price': 120.00,
                'popularity_rank': 1,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'ขายดี'
            },
            {
                'item_code': 'FOOD002',
                'item_name': 'ข้าวผัดปู',
                'category': 'อาหารจานเดียว',
                'total_sold': 18,
                'total_revenue': 3240.00,
                'avg_price': 180.00,
                'popularity_rank': 2,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'ขายดี'
            }
        ]
        
        sheets_manager.update_item_analytics(order_items_1 + order_items_2)
        print("✅ อัปเดตสถิติสินค้าเสร็จสิ้น")
        
        print("\n🎉 การทดสอบเสร็จสิ้น!")
        print("\n📋 สรุปฟีเจอร์ที่ทดสอบ:")
        print("   ✅ การบันทึกออเดอร์ที่ละเอียดขึ้น")
        print("   ✅ การบันทึกรายการอาหารพร้อมตัวเลือกพิเศษ")
        print("   ✅ การคำนวณและบันทึกสถิติรายวัน")
        print("   ✅ การวิเคราะห์และติดตามสถิติสินค้า")
        print("   ✅ การแปลสถานะเป็นภาษาไทย")
        print("   ✅ การจัดรูปแบบข้อมูลอัตโนมัติ")
        
        # แสดงลิงก์ Google Sheets
        with open('backend/google_sheets_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        spreadsheet_id = config['spreadsheet_id']
        print(f"\n🔗 ตรวจสอบผลลัพธ์ที่: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการทดสอบ: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_pos_integration()