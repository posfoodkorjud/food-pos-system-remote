#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script สำหรับรีเซ็ต Google Sheets ทั้งหมด
ลบข้อมูลและ sheets ทั้งหมด แล้วสร้างใหม่ตามรูปแบบที่กำหนด
"""

import sys
import os

# เพิ่ม path ของ backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from google_sheets import (
    reset_google_sheets,
    clear_all_sheets_data,
    delete_all_sheets,
    is_google_sheets_enabled,
    google_sheets_manager
)

def main():
    """
    ฟังก์ชันหลักสำหรับรีเซ็ต Google Sheets
    """
    print("=" * 60)
    print("🔄 Google Sheets Reset Tool")
    print("=" * 60)
    
    # ตรวจสอบการเชื่อมต่อ
    if not is_google_sheets_enabled():
        print("❌ Google Sheets ไม่ได้เปิดใช้งานหรือไม่สามารถเชื่อมต่อได้")
        print("กรุณาตรวจสอบ:")
        print("1. ไฟล์ credentials.json")
        print("2. ไฟล์ google_sheets_config.json")
        print("3. การตั้งค่า Google Sheets API")
        return False
    
    print(f"✅ เชื่อมต่อ Google Sheets สำเร็จ")
    print(f"📊 Spreadsheet ID: {google_sheets_manager.spreadsheet_id}")
    print()
    
    # แสดงตัวเลือก
    print("เลือกการดำเนินการ:")
    print("1. ลบข้อมูลทั้งหมด (เก็บ headers)")
    print("2. ลบ sheets ทั้งหมด")
    print("3. รีเซ็ตทั้งหมด (ลบและสร้างใหม่)")
    print("4. ยกเลิก")
    print()
    
    try:
        choice = input("กรุณาเลือก (1-4): ").strip()
        
        if choice == "1":
            print("\n🗑️  กำลังลบข้อมูลทั้งหมด...")
            if clear_all_sheets_data():
                print("✅ ลบข้อมูลทั้งหมดสำเร็จ")
            else:
                print("❌ เกิดข้อผิดพลาดในการลบข้อมูล")
                
        elif choice == "2":
            print("\n🗑️  กำลังลบ sheets ทั้งหมด...")
            if delete_all_sheets():
                print("✅ ลบ sheets ทั้งหมดสำเร็จ")
            else:
                print("❌ เกิดข้อผิดพลาดในการลบ sheets")
                
        elif choice == "3":
            print("\n🔄 กำลังรีเซ็ตทั้งหมด...")
            if reset_google_sheets():
                print("✅ รีเซ็ต Google Sheets สำเร็จ")
                print("\n📋 Sheets ที่สร้างใหม่:")
                print("   • Orders - ข้อมูลออเดอร์หลัก")
                print("   • Order_Items - รายการสินค้าในออเดอร์")
                print("   • Daily_Summary - สรุปยอดขายรายวัน")
                print("   • Monthly_Summary - สรุปยอดขายรายเดือน")
                print("   • Item_Analytics - วิเคราะห์ยอดขายสินค้า")
            else:
                print("❌ เกิดข้อผิดพลาดในการรีเซ็ต")
                
        elif choice == "4":
            print("\n❌ ยกเลิกการดำเนินการ")
            
        else:
            print("\n❌ ตัวเลือกไม่ถูกต้อง")
            
    except KeyboardInterrupt:
        print("\n\n❌ ยกเลิกการดำเนินการ")
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 เสร็จสิ้นการดำเนินการ")
    print("=" * 60)

if __name__ == "__main__":
    main()