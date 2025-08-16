#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับการกู้คืนเมนูอัตโนมัติ
ใช้เมื่อพบปัญหากับเมนูและต้องการกู้คืนเป็นสถานะที่ถูกต้อง
"""

import sqlite3
import os
import shutil
from datetime import datetime
import json

def find_latest_backup():
    """ค้นหาไฟล์ backup ล่าสุด"""
    
    backup_dir = "menu_backups"
    
    if not os.path.exists(backup_dir):
        print(f"❌ ไม่พบโฟลเดอร์ backup: {backup_dir}")
        return None, None
    
    # ค้นหาไฟล์ .db และ .json ล่าสุด
    db_files = []
    json_files = []
    
    for file in os.listdir(backup_dir):
        if file.endswith('.db'):
            db_files.append(os.path.join(backup_dir, file))
        elif file.endswith('.json'):
            json_files.append(os.path.join(backup_dir, file))
    
    if not db_files:
        print("❌ ไม่พบไฟล์ backup ฐานข้อมูล")
        return None, None
    
    # เรียงตามวันที่แก้ไขล่าสุด
    latest_db = max(db_files, key=os.path.getmtime)
    latest_json = max(json_files, key=os.path.getmtime) if json_files else None
    
    return latest_db, latest_json

def backup_current_database():
    """สำรองฐานข้อมูลปัจจุบันก่อนกู้คืน"""
    
    db_path = "A_FOOD_POS/FOOD_POS/pos_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบไฟล์ฐานข้อมูล: {db_path}")
        return False
    
    # สร้างโฟลเดอร์ backup หากไม่มี
    backup_dir = "emergency_backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    # สร้างชื่อไฟล์ backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"emergency_backup_{timestamp}.db")
    
    try:
        shutil.copy2(db_path, backup_file)
        print(f"✅ สำรองฐานข้อมูลปัจจุบัน: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ ไม่สามารถสำรองฐานข้อมูลได้: {e}")
        return False

def restore_from_backup(backup_db_path):
    """กู้คืนฐานข้อมูลจากไฟล์ backup"""
    
    db_path = "A_FOOD_POS/FOOD_POS/pos_database.db"
    
    if not os.path.exists(backup_db_path):
        print(f"❌ ไม่พบไฟล์ backup: {backup_db_path}")
        return False
    
    try:
        # สำรองฐานข้อมูลปัจจุบันก่อน
        emergency_backup = backup_current_database()
        if not emergency_backup:
            print("⚠️ ไม่สามารถสำรองฐานข้อมูลปัจจุบันได้ แต่จะดำเนินการกู้คืนต่อไป")
        
        # คัดลอกไฟล์ backup มาแทนที่
        shutil.copy2(backup_db_path, db_path)
        print(f"✅ กู้คืนฐานข้อมูลเรียบร้อย")
        
        # ตรวจสอบผลลัพธ์
        verify_restoration()
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการกู้คืน: {e}")
        return False

def verify_restoration():
    """ตรวจสอบผลลัพธ์หลังการกู้คืน"""
    
    db_path = "A_FOOD_POS/FOOD_POS/pos_database.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ตรวจสอบจำนวนหมวดหมู่และเมนู
        cursor.execute("SELECT COUNT(*) FROM menu_categories WHERE is_active = 1")
        category_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM menu_items WHERE is_available = 1")
        menu_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(price), MAX(price) FROM menu_items WHERE is_available = 1")
        min_price, max_price = cursor.fetchone()
        
        conn.close()
        
        print(f"\n📊 ผลลัพธ์หลังการกู้คืน:")
        print(f"- หมวดหมู่: {category_count} รายการ")
        print(f"- เมนู: {menu_count} รายการ")
        print(f"- ช่วงราคา: {min_price}-{max_price} บาท")
        
        # ตรวจสอบความถูกต้อง
        if category_count == 4 and menu_count == 77 and min_price >= 15 and max_price <= 59:
            print("✅ การกู้คืนสำเร็จ! เมนูอยู่ในสภาพที่ถูกต้อง")
            return True
        else:
            print("⚠️ การกู้คืนอาจไม่สมบูรณ์ กรุณาตรวจสอบเพิ่มเติม")
            return False
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการตรวจสอบ: {e}")
        return False

def clean_menu_data():
    """ทำความสะอาดข้อมูลเมนูที่มีปัญหา"""
    
    db_path = "A_FOOD_POS/FOOD_POS/pos_database.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🧹 เริ่มทำความสะอาดข้อมูลเมนู...")
        
        # 1. ลบเมนูที่มีชื่อซ้ำ (เก็บรายการแรก)
        cursor.execute("""
            DELETE FROM menu_items 
            WHERE item_id NOT IN (
                SELECT MIN(item_id) 
                FROM menu_items 
                WHERE is_available = 1
                GROUP BY name
            ) AND is_available = 1
        """)
        deleted_duplicates = cursor.rowcount
        
        # 2. ลบเมนูที่มีราคานอกช่วง
        cursor.execute("""
            UPDATE menu_items 
            SET is_available = 0 
            WHERE (price < 15 OR price > 59) AND is_available = 1
        """)
        disabled_price_issues = cursor.rowcount
        
        # 3. ลบหมวดหมู่ที่มีชื่อซ้ำ (เก็บรายการแรก)
        cursor.execute("""
            UPDATE menu_categories 
            SET is_active = 0 
            WHERE category_id NOT IN (
                SELECT MIN(category_id) 
                FROM menu_categories 
                WHERE is_active = 1
                GROUP BY name
            ) AND is_active = 1
        """)
        disabled_duplicate_categories = cursor.rowcount
        
        # 4. ปิดการใช้งานเมนูที่ไม่มีหมวดหมู่
        cursor.execute("""
            UPDATE menu_items 
            SET is_available = 0 
            WHERE category_id NOT IN (
                SELECT category_id FROM menu_categories WHERE is_active = 1
            ) AND is_available = 1
        """)
        disabled_orphan_items = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"✅ ทำความสะอาดเรียบร้อย:")
        print(f"- ลบเมนูชื่อซ้ำ: {deleted_duplicates} รายการ")
        print(f"- ปิดเมนูราคาผิดปกติ: {disabled_price_issues} รายการ")
        print(f"- ปิดหมวดหมู่ซ้ำ: {disabled_duplicate_categories} รายการ")
        print(f"- ปิดเมนูไม่มีหมวดหมู่: {disabled_orphan_items} รายการ")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการทำความสะอาด: {e}")
        return False

def auto_recovery():
    """กู้คืนเมนูอัตโนมัติ"""
    
    print("🚨 เริ่มกระบวนการกู้คืนเมนูอัตโนมัติ")
    print("="*50)
    
    # 1. ค้นหาไฟล์ backup ล่าสุด
    latest_db, latest_json = find_latest_backup()
    
    if not latest_db:
        print("❌ ไม่พบไฟล์ backup ไม่สามารถกู้คืนได้")
        print("💡 ลองใช้ clean_menu_data() เพื่อทำความสะอาดข้อมูลแทน")
        return False
    
    print(f"📁 พบไฟล์ backup: {os.path.basename(latest_db)}")
    
    # 2. แสดงข้อมูลจาก backup
    if latest_json and os.path.exists(latest_json):
        try:
            with open(latest_json, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            print(f"📊 ข้อมูลใน backup:")
            print(f"- เมนูทั้งหมด: {len(backup_data)} รายการ")
            
            # แสดงตัวอย่างเมนู
            if backup_data:
                sample_item = backup_data[0]
                print(f"- ตัวอย่าง: {sample_item.get('name', 'N/A')} ({sample_item.get('price', 'N/A')} บาท)")
        
        except Exception as e:
            print(f"⚠️ ไม่สามารถอ่านไฟล์ JSON ได้: {e}")
    
    # 3. ยืนยันการกู้คืน
    confirm = input("\n❓ ต้องการดำเนินการกู้คืนหรือไม่? (y/n): ").lower().strip()
    
    if confirm != 'y':
        print("❌ ยกเลิกการกู้คืน")
        return False
    
    # 4. ดำเนินการกู้คืน
    success = restore_from_backup(latest_db)
    
    if success:
        print("\n🎉 การกู้คืนเมนูสำเร็จ!")
        print("💡 แนะนำให้รีสตาร์ทเซิร์ฟเวอร์เพื่อให้การเปลี่ยนแปลงมีผล")
        return True
    else:
        print("\n❌ การกู้คืนล้มเหลว")
        return False

def emergency_clean():
    """ทำความสะอาดข้อมูลเมื่อไม่มี backup"""
    
    print("🧹 เริ่มกระบวนการทำความสะอาดฉุกเฉิน")
    print("="*50)
    
    # สำรองข้อมูลปัจจุบันก่อน
    emergency_backup = backup_current_database()
    if emergency_backup:
        print(f"✅ สำรองข้อมูลปัจจุบัน: {emergency_backup}")
    
    # ทำความสะอาด
    success = clean_menu_data()
    
    if success:
        # ตรวจสอบผลลัพธ์
        verify_restoration()
        print("\n💡 แนะนำให้รีสตาร์ทเซิร์ฟเวอร์เพื่อให้การเปลี่ยนแปลงมีผล")
        return True
    else:
        print("\n❌ การทำความสะอาดล้มเหลว")
        return False

if __name__ == "__main__":
    print("🚨 เครื่องมือกู้คืนเมนูอัตโนมัติ")
    print("="*40)
    
    print("เลือกการดำเนินการ:")
    print("1. กู้คืนจาก backup อัตโนมัติ")
    print("2. ทำความสะอาดข้อมูลเมนู")
    print("3. ตรวจสอบไฟล์ backup ที่มี")
    
    choice = input("\nเลือก (1-3): ").strip()
    
    if choice == '1':
        auto_recovery()
    elif choice == '2':
        emergency_clean()
    elif choice == '3':
        latest_db, latest_json = find_latest_backup()
        if latest_db:
            print(f"📁 ไฟล์ backup ล่าสุด:")
            print(f"- Database: {latest_db}")
            if latest_json:
                print(f"- JSON: {latest_json}")
        else:
            print("❌ ไม่พบไฟล์ backup")
    else:
        print("❌ ตัวเลือกไม่ถูกต้อง")