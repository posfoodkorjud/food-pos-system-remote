#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับ restore เมนูจากไฟล์ backup
⚠️ ใช้ด้วยความระมัดระวัง!
"""

import sqlite3
import shutil
import os
import json
from datetime import datetime
import glob

def list_backup_files():
    """แสดงรายการไฟล์ backup ที่มีอยู่"""
    backup_dir = "menu_backups"
    
    if not os.path.exists(backup_dir):
        print("❌ ไม่พบโฟลเดอร์ backup")
        return []
    
    # หาไฟล์ backup ฐานข้อมูล
    db_backups = glob.glob(os.path.join(backup_dir, "pos_database_backup_*.db"))
    json_backups = glob.glob(os.path.join(backup_dir, "menu_data_backup_*.json"))
    
    print("📋 ไฟล์ backup ที่มีอยู่:")
    print("\n🗄️ Database backups:")
    for i, backup in enumerate(db_backups, 1):
        filename = os.path.basename(backup)
        timestamp = filename.replace("pos_database_backup_", "").replace(".db", "")
        formatted_time = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {i}. {filename} ({formatted_time})")
    
    print("\n📄 JSON backups:")
    for i, backup in enumerate(json_backups, 1):
        filename = os.path.basename(backup)
        timestamp = filename.replace("menu_data_backup_", "").replace(".json", "")
        formatted_time = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {i}. {filename} ({formatted_time})")
    
    return db_backups, json_backups

def restore_database_backup(backup_file):
    """Restore ฐานข้อมูลทั้งหมดจากไฟล์ backup"""
    
    db_path = "A_FOOD_POS/FOOD_POS/pos_database.db"
    
    if not os.path.exists(backup_file):
        print(f"❌ ไม่พบไฟล์ backup: {backup_file}")
        return False
    
    try:
        # สร้าง backup ของฐานข้อมูลปัจจุบันก่อน restore
        current_backup = f"pos_database_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, current_backup)
        print(f"✅ สร้าง backup ฐานข้อมูลปัจจุบัน: {current_backup}")
        
        # Restore ฐานข้อมูล
        shutil.copy2(backup_file, db_path)
        print(f"✅ Restore ฐานข้อมูลจาก: {backup_file}")
        
        # ตรวจสอบผลลัพธ์
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM menu_items WHERE is_available = 1")
        menu_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM menu_categories WHERE is_active = 1")
        category_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"📊 ผลลัพธ์หลัง restore:")
        print(f"  - จำนวนหมวดหมู่: {category_count}")
        print(f"  - จำนวนเมนู: {menu_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการ restore: {e}")
        return False

def view_backup_info(json_backup_file):
    """ดูข้อมูลใน backup JSON"""
    
    if not os.path.exists(json_backup_file):
        print(f"❌ ไม่พบไฟล์: {json_backup_file}")
        return
    
    try:
        with open(json_backup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📄 ข้อมูลใน backup: {os.path.basename(json_backup_file)}")
        print(f"📅 วันที่สร้าง: {data.get('backup_date', 'ไม่ระบุ')}")
        
        if 'summary' in data:
            summary = data['summary']
            print(f"📊 สรุป:")
            print(f"  - จำนวนเมนูทั้งหมด: {summary.get('total_menu_items', 0)}")
            print(f"  - เมนูที่พร้อมขาย: {summary.get('available_items', 0)}")
            if 'price_range' in summary:
                price_range = summary['price_range']
                print(f"  - ช่วงราคา: {price_range.get('min', 0)}-{price_range.get('max', 0)} บาท")
        
        if 'categories' in data:
            print(f"📂 หมวดหมู่: {len(data['categories'])} รายการ")
            for cat in data['categories'][:5]:  # แสดง 5 รายการแรก
                print(f"  - {cat.get('name', 'ไม่ระบุชื่อ')}")
            if len(data['categories']) > 5:
                print(f"  ... และอีก {len(data['categories']) - 5} รายการ")
        
        if 'menu_items' in data:
            print(f"🍽️ เมนู: {len(data['menu_items'])} รายการ")
            for item in data['menu_items'][:5]:  # แสดง 5 รายการแรก
                name = item.get('name', 'ไม่ระบุชื่อ')
                price = item.get('price', 0)
                print(f"  - {name} ({price} บาท)")
            if len(data['menu_items']) > 5:
                print(f"  ... และอีก {len(data['menu_items']) - 5} รายการ")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")

def main():
    """ฟังก์ชันหลัก"""
    print("🔄 เครื่องมือ Restore Menu Backup")
    print("⚠️ กรุณาใช้ด้วยความระมัดระวัง!")
    print("="*50)
    
    db_backups, json_backups = list_backup_files()
    
    if not db_backups and not json_backups:
        print("❌ ไม่พบไฟล์ backup")
        return
    
    print("\n📋 เลือกการดำเนินการ:")
    print("1. ดูข้อมูลใน JSON backup")
    print("2. Restore ฐานข้อมูลจาก DB backup (⚠️ อันตราย!)")
    print("3. ออกจากโปรแกรม")
    
    choice = input("\nเลือก (1-3): ").strip()
    
    if choice == "1":
        if json_backups:
            print("\nเลือกไฟล์ JSON backup:")
            for i, backup in enumerate(json_backups, 1):
                filename = os.path.basename(backup)
                print(f"{i}. {filename}")
            
            try:
                file_choice = int(input("เลือกไฟล์ (หมายเลข): ")) - 1
                if 0 <= file_choice < len(json_backups):
                    view_backup_info(json_backups[file_choice])
                else:
                    print("❌ หมายเลขไม่ถูกต้อง")
            except ValueError:
                print("❌ กรุณาใส่หมายเลข")
        else:
            print("❌ ไม่พบไฟล์ JSON backup")
    
    elif choice == "2":
        print("\n⚠️ การ restore ฐานข้อมูลจะเขียนทับข้อมูลปัจจุบัน!")
        confirm = input("ยืนยันการดำเนินการ (พิมพ์ 'YES' เพื่อยืนยัน): ")
        
        if confirm == "YES":
            if db_backups:
                print("\nเลือกไฟล์ DB backup:")
                for i, backup in enumerate(db_backups, 1):
                    filename = os.path.basename(backup)
                    print(f"{i}. {filename}")
                
                try:
                    file_choice = int(input("เลือกไฟล์ (หมายเลข): ")) - 1
                    if 0 <= file_choice < len(db_backups):
                        restore_database_backup(db_backups[file_choice])
                        print("\n⚠️ กรุณา restart server เพื่อให้การเปลี่ยนแปลงมีผล")
                    else:
                        print("❌ หมายเลขไม่ถูกต้อง")
                except ValueError:
                    print("❌ กรุณาใส่หมายเลข")
            else:
                print("❌ ไม่พบไฟล์ DB backup")
        else:
            print("❌ ยกเลิกการ restore")
    
    elif choice == "3":
        print("👋 ออกจากโปรแกรม")
    
    else:
        print("❌ ตัวเลือกไม่ถูกต้อง")

if __name__ == "__main__":
    main()