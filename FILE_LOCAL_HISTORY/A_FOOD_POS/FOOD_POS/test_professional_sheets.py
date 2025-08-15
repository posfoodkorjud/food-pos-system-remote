#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบ Google Sheets Integration แบบมืออาชีพ
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.google_sheets import google_sheets_manager
from datetime import datetime
import time

def test_professional_features():
    """
    ทดสอบฟีเจอร์ใหม่ที่เพิ่มเข้ามา
    """
    print("=== ทดสอบ Google Sheets แบบมืออาชีพ ===")
    
    # ตรวจสอบการเชื่อมต่อ
    if not google_sheets_manager.enabled:
        print("❌ Google Sheets ไม่ได้เปิดใช้งาน")
        return False
    
    if not google_sheets_manager.test_connection():
        print("❌ ไม่สามารถเชื่อมต่อ Google Sheets ได้")
        return False
    
    print("✅ เชื่อมต่อ Google Sheets สำเร็จ")
    
    # สร้างหัวตารางใหม่
    print("\n📋 กำลังสร้างหัวตารางแบบมืออาชีพ...")
    if google_sheets_manager.create_headers_if_needed():
        print("✅ สร้างหัวตารางสำเร็จ")
    else:
        print("❌ ไม่สามารถสร้างหัวตารางได้")
        return False
    
    # ทดสอบการบันทึกออเดอร์แบบใหม่
    print("\n🍽️ กำลังทดสอบการบันทึกออเดอร์...")
    test_order_data = {
        'order_id': 200,
        'table_id': 5,
        'session_id': 'session_200',
        'status': 'completed',
        'total_amount': 450.0,
        'payment_method': 'เงินสด',
        'customer_count': 3,
        'order_type': 'Dine-in',
        'created_at': '2024-01-15 12:30:00',
        'completed_at': '2024-01-15 12:48:00'
    }
    
    if google_sheets_manager.sync_order(test_order_data):
        print("✅ บันทึกออเดอร์สำเร็จ")
    else:
        print("❌ ไม่สามารถบันทึกออเดอร์ได้")
    
    # ทดสอบการบันทึกรายการอาหารแบบใหม่
    print("\n🥘 กำลังทดสอบการบันทึกรายการอาหาร...")
    test_order_items = [
        {
            'order_item_id': 301,
            'order_id': 200,
            'item_id': 15,
            'category': 'อาหารจานหลัก',
            'item_name': 'ข้าวผัดกุ้ง',
            'quantity': 2,
            'unit_price': 120.0,
            'total_price': 240.0,
            'customer_request': 'ไม่ใส่ผักชี',
            'special_options': 'เผ็ดน้อย',
            'status': 'completed'
        },
        {
            'order_item_id': 302,
            'order_id': 200,
            'item_id': 8,
            'category': 'เครื่องดื่ม',
            'item_name': 'น้ำส้มคั้นสด',
            'quantity': 3,
            'unit_price': 70.0,
            'total_price': 210.0,
            'customer_request': '',
            'special_options': 'น้ำแข็งน้อย',
            'status': 'completed'
        }
    ]
    
    if google_sheets_manager.sync_order_items(test_order_items):
        print("✅ บันทึกรายการอาหารสำเร็จ")
    else:
        print("❌ ไม่สามารถบันทึกรายการอาหารได้")
    
    # ทดสอบการบันทึกสถิติรายวัน
    print("\n📊 กำลังทดสอบการบันทึกสถิติรายวัน...")
    daily_stats = {
        'total_orders': 28,
        'completed_orders': 26,
        'cancelled_orders': 2,
        'total_revenue': 3200.0,
        'total_items_sold': 52,
        'average_order_value': 123.1,
        'peak_hour': '12:00-13:00',
        'most_popular_item': 'ข้าวผัดกุ้ง',
        'total_tables_served': 18,
        'average_service_time': 16
    }
    
    if google_sheets_manager.sync_daily_summary('2024-01-15', daily_stats):
        print("✅ บันทึกสถิติรายวันสำเร็จ")
    else:
        print("❌ ไม่สามารถบันทึกสถิติรายวันได้")
    
    print("\n🎉 การทดสอบเสร็จสิ้น!")
    print("\n📝 สิ่งที่ปรับปรุงใหม่:")
    print("   • หัวตารางที่ครบถ้วนและมีสีสัน")
    print("   • ข้อมูลออเดอร์ที่ละเอียดมากขึ้น (วันที่/เวลาแยก, ระยะเวลาบริการ)")
    print("   • รายการอาหารที่มีการคำนวณส่วนลด")
    print("   • สถิติรายวันที่ครบถ้วน (ชั่วโมงยอดนิยม, สินค้าขายดี)")
    print("   • การแปลสถานะเป็นภาษาไทย")
    print("   • Sheet ใหม่: Monthly_Summary และ Item_Analytics")
    print("   • การจัดรูปแบบอัตโนมัติ")
    
    return True

def create_sample_monthly_data():
    """
    สร้างข้อมูลตัวอย่างสำหรับ Monthly Summary
    """
    print("\n📅 กำลังสร้างข้อมูลสรุปรายเดือน...")
    
    monthly_data = [
        ['2024-01', 850, 95000.0, 3064.5, '2024-01-15', '2024-01-03', 12.5, 'ข้าวผัดกุ้ง, ส้มตำ, น้ำส้มคั้น']
    ]
    
    if google_sheets_manager.append_to_sheet('Monthly_Summary', monthly_data):
        print("✅ สร้างข้อมูลสรุปรายเดือนสำเร็จ")
    else:
        print("❌ ไม่สามารถสร้างข้อมูลสรุปรายเดือนได้")

def create_sample_analytics_data():
    """
    สร้างข้อมูลตัวอย่างสำหรับ Item Analytics
    """
    print("\n📈 กำลังสร้างข้อมูลวิเคราะห์สินค้า...")
    
    analytics_data = [
        ['ข้าวผัดกุ้ง', 'อาหารจานหลัก', 156, 18720.0, 120.0, 1, '2024-01-15', 95.2, 65.0],
        ['ส้มตำ', 'อาหารจานหลัก', 134, 10720.0, 80.0, 2, '2024-01-15', 87.3, 70.0],
        ['น้ำส้มคั้นสด', 'เครื่องดื่ม', 98, 6860.0, 70.0, 3, '2024-01-15', 78.9, 80.0]
    ]
    
    if google_sheets_manager.append_to_sheet('Item_Analytics', analytics_data):
        print("✅ สร้างข้อมูลวิเคราะห์สินค้าสำเร็จ")
    else:
        print("❌ ไม่สามารถสร้างข้อมูลวิเคราะห์สินค้าได้")

if __name__ == "__main__":
    try:
        # ทดสอบฟีเจอร์หลัก
        if test_professional_features():
            # รอสักครู่แล้วสร้างข้อมูลตัวอย่าง
            time.sleep(2)
            create_sample_monthly_data()
            time.sleep(1)
            create_sample_analytics_data()
            
            print("\n🌟 ทุกอย่างเสร็จสิ้นแล้ว! ตรวจสอบ Google Sheets ของคุณ")
        else:
            print("\n❌ การทดสอบล้มเหลว")
            
    except Exception as e:
        print(f"\n💥 เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()