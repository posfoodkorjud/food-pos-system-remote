#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update Menu Script - Direct Database Access
สคริปต์อัปเดตเมนูโดยเข้าถึงฐานข้อมูลโดยตรง
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from backend.database import DatabaseManager
except ImportError as e:
    print(f"Error importing DatabaseManager: {e}")
    sys.exit(1)

def clear_existing_menu():
    """ลบเมนูและหมวดหมู่เดิมทั้งหมด"""
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # ลบรายการเมนูทั้งหมด
        cursor.execute("DELETE FROM menu_items")
        print("✅ ลบรายการเมนูเดิมทั้งหมดแล้ว")
        
        # ลบหมวดหมู่ทั้งหมด
        cursor.execute("DELETE FROM menu_categories")
        print("✅ ลบหมวดหมู่เดิมทั้งหมดแล้ว")

        # รีเซ็ต autoincrement
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='menu_categories'")
        print("✅ รีเซ็ต ID ของหมวดหมู่แล้ว")
        
        conn.commit()

        # จัดระเบียบฐานข้อมูล
        print("🧹 กำลังจัดระเบียบฐานข้อมูล...")
        conn.execute("VACUUM")
        print("✅ จัดระเบียบฐานข้อมูลเสร็จสิ้น")

        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ เกิดข้อผิดพลาดขณะลบเมนูเดิม: {e}")
        return False
    finally:
        conn.close()

def add_categories():
    """เพิ่มหมวดหมู่ใหม่"""
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    categories = [
        ("ของหวาน", "🍰", True),
        ("ยำ/สลัด", "🥗", True),
        ("อาหารจานเดียว", "🥘", True),
        ("อาหารทานเล่น", "🍢", True),
        ("เครื่องดื่ม", "🍹", True)
    ]
    
    for name, icon, is_active in categories:
        cursor.execute(
            "INSERT INTO menu_categories (name, description, is_active) VALUES (?, ?, ?)",
            (name, icon, is_active)
        )
    
    print("✅ เพิ่มหมวดหมู่ใหม่ 5 หมวดหมู่แล้ว")
    conn.commit()
    conn.close()

def add_menu_items():
    """เพิ่มรายการอาหารใหม่"""
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    menu_items = [
        # 1. หมวดหมู่ของหวาน (10 รายการ)
        ("กล้วยทอด", 30.0, 1, True),
        ("ขนมปังปิ้งเนยน้ำตาล", 30.0, 1, True),
        ("ชีสเค้ก", 55.0, 1, True),
        ("บิงซูผลไม้", 65.0, 1, True),
        ("ปังเย็นช็อกโกแลต", 45.0, 1, True),
        ("เครปเย็น", 50.0, 1, True),
        ("เฉาก๊วยนมสด", 35.0, 1, True),
        ("แพนเค้กกล้วยหอม", 50.0, 1, True),
        ("โรตีใส่กล้วย", 40.0, 1, True),
        ("ไอศกรีมกะทิสด", 40.0, 1, True),

        # 2. หมวดหมู่ยำ/สลัด (10 รายการ)
        ("ซีซาร์สลัด", 75.0, 2, True),
        ("ยำขนมจีน", 65.0, 2, True),
        ("ยำมาม่า", 65.0, 2, True),
        ("ยำรวมทะเล", 85.0, 2, True),
        ("ยำวุ้นเส้นหมูสับ", 65.0, 2, True),
        ("ยำไข่ดาว", 60.0, 2, True),
        ("ยำแซลมอน", 90.0, 2, True),
        ("ยำไส้กรอก", 60.0, 2, True),
        ("ยำหมูยอ", 60.0, 2, True),
        ("ยำเห็ดรวม", 65.0, 2, True),

        # 3. หมวดหมู่อาหารจานเดียว (10 รายการ)
        ("ข้าวกระเพราหมูสับไข่ดาว", 65.0, 3, True),
        ("ข้าวกะเพราเต้าหู้", 60.0, 3, True),
        ("ข้าวคลุกกะปิ", 65.0, 3, True),
        ("ข้าวคั่วกลิ้งหมู", 70.0, 3, True),
        ("ข้าวน้ำพริกลงเรือ", 70.0, 3, True),
        ("ข้าวผัดหมู", 60.0, 3, True),
        ("ข้าวราดเขียวหวานไก่", 70.0, 3, True),
        ("ข้าวหน้าไก่เทอริยากิ", 75.0, 3, True),
        ("ข้าวหมูกระเทียม", 60.0, 3, True),
        ("ข้าวไข่เจียวหมูสับ", 55.0, 3, True),

        # 4. หมวดหมู่อาหารทานเล่น (10 รายการ)
        ("ข้าวโพดชีส", 50.0, 4, True),
        ("นักเก็ตไก่", 50.0, 4, True),
        ("ปีกไก่ทอดน้ำปลา", 60.0, 4, True),
        ("ลูกชิ้นลวกจิ้ม", 45.0, 4, True),
        ("หมูทอดจิ้มแจ่ว", 60.0, 4, True),
        ("เกี๊ยวซ่าทอด", 50.0, 4, True),
        ("เฟรนช์ฟรายส์", 45.0, 4, True),
        ("แหนมคลุก", 55.0, 4, True),
        ("ไก่ทอดเกลือ", 55.0, 4, True),
        ("ไก่ป๊อป", 55.0, 4, True),

        # 5. หมวดหมู่เครื่องดื่ม (10 รายการ)
        ("กาแฟเย็น", 40.0, 5, True),
        ("ชามะนาว", 35.0, 5, True),
        ("ชาเขียวเย็น", 35.0, 5, True),
        ("ชาไทยเย็น", 35.0, 5, True),
        ("นมชมพู", 35.0, 5, True),
        ("น้ำผึ้งมะนาวโซดา", 45.0, 5, True),
        ("น้ำอัญชัน / เก๊กฮวย / กระเจี๊ยบ", 30.0, 5, True),
        ("ม็อกเทลลิ้นจี่โซดา", 50.0, 5, True),
        ("อเมริกาโน่", 40.0, 5, True),
        ("โกโก้เย็น", 40.0, 5, True)
    ]
    
    for name, price, category_id, is_available in menu_items:
        cursor.execute(
            "INSERT INTO menu_items (name, price, category_id, is_available) VALUES (?, ?, ?, ?)",
            (name, price, category_id, is_available)
        )
    
    print(f"✅ เพิ่มรายการอาหารใหม่ {len(menu_items)} รายการแล้ว")
    conn.commit()
    conn.close()

def main():
    """ฟังก์ชันหลัก"""
    print("\n" + "="*60)
    print("🍽️ FOOD POS SYSTEM - MENU UPDATE")
    print("   อัปเดตเมนูอาหารใหม่")
    print("="*60)
    
    try:
        print("\n🗑️ กำลังลบเมนูเดิม...")
        clear_existing_menu()
        
        print("\n📂 กำลังเพิ่มหมวดหมู่ใหม่...")
        add_categories()
        
        print("\n🍽️ กำลังเพิ่มรายการอาหารใหม่...")
        add_menu_items()
        
        print("\n" + "="*60)
        print("✅ อัปเดตเมนูเสร็จสิ้น!")
        print("📊 สรุป:")
        print("   - หมวดหมู่: 5 หมวดหมู่")
        print("   - รายการอาหาร: 50 รายการ")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()