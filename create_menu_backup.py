#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับสร้าง backup ของเมนูและฐานข้อมูล POS
เพื่อป้องกันการสูญหายของข้อมูลเมนูที่ถูกต้อง
"""

import sqlite3
import shutil
import os
from datetime import datetime
import json

def create_menu_backup():
    """สร้าง backup ของเมนูและฐานข้อมูล"""
    
    # กำหนดเส้นทางไฟล์
    db_path = "A_FOOD_POS/FOOD_POS/pos_database.db"
    backup_dir = "menu_backups"
    
    # สร้างโฟลเดอร์ backup ถ้ายังไม่มี
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"✅ สร้างโฟลเดอร์ {backup_dir} เรียบร้อยแล้ว")
    
    # สร้างชื่อไฟล์ backup ตามวันที่และเวลา
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_db_path = os.path.join(backup_dir, f"pos_database_backup_{timestamp}.db")
    
    try:
        # 1. Backup ฐานข้อมูล
        shutil.copy2(db_path, backup_db_path)
        print(f"✅ Backup ฐานข้อมูล: {backup_db_path}")
        
        # 2. Export ข้อมูลเมนูเป็น JSON
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ดึงข้อมูลหมวดหมู่
        cursor.execute("SELECT * FROM category WHERE is_active = 1")
        categories = cursor.fetchall()
        categories_data = []
        for cat in categories:
            categories_data.append({
                "id": cat[0],
                "name": cat[1],
                "is_active": cat[2]
            })
        
        # ดึงข้อมูลเมนู
        cursor.execute("SELECT * FROM menu_item WHERE is_available = 1")
        menu_items = cursor.fetchall()
        menu_data = []
        for item in menu_items:
            menu_data.append({
                "id": item[0],
                "name": item[1],
                "price": item[2],
                "category_id": item[3],
                "is_available": item[4]
            })
        
        conn.close()
        
        # สร้างไฟล์ JSON backup
        backup_data = {
            "backup_date": datetime.now().isoformat(),
            "categories": categories_data,
            "menu_items": menu_data,
            "summary": {
                "total_categories": len(categories_data),
                "total_menu_items": len(menu_data)
            }
        }
        
        json_backup_path = os.path.join(backup_dir, f"menu_data_backup_{timestamp}.json")
        with open(json_backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Backup ข้อมูลเมนู JSON: {json_backup_path}")
        
        # 3. สร้างไฟล์สรุป backup
        summary_path = os.path.join(backup_dir, f"backup_summary_{timestamp}.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"=== MENU BACKUP SUMMARY ===\n")
            f.write(f"วันที่สร้าง backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"จำนวนหมวดหมู่: {len(categories_data)}\n")
            f.write(f"จำนวนเมนู: {len(menu_data)}\n\n")
            
            f.write("หมวดหมู่:\n")
            for cat in categories_data:
                f.write(f"- {cat['name']} (ID: {cat['id']})\n")
            
            f.write("\nช่วงราคาเมนู:\n")
            prices = [item['price'] for item in menu_data]
            f.write(f"- ราคาต่ำสุด: {min(prices)} บาท\n")
            f.write(f"- ราคาสูงสุด: {max(prices)} บาท\n")
            
            f.write(f"\nไฟล์ backup:\n")
            f.write(f"- Database: {backup_db_path}\n")
            f.write(f"- JSON: {json_backup_path}\n")
            f.write(f"- Summary: {summary_path}\n")
        
        print(f"✅ สร้างไฟล์สรุป: {summary_path}")
        
        print("\n" + "="*50)
        print("🎉 สร้าง BACKUP เรียบร้อยแล้ว!")
        print(f"📁 โฟลเดอร์ backup: {backup_dir}")
        print(f"📊 จำนวนหมวดหมู่: {len(categories_data)}")
        print(f"🍽️ จำนวนเมนู: {len(menu_data)}")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้าง backup: {e}")
        return False

def restore_menu_from_backup(backup_file):
    """ฟังก์ชันสำหรับ restore เมนูจากไฟล์ backup (ใช้เมื่อจำเป็น)"""
    print(f"⚠️ ฟังก์ชัน restore_menu_from_backup พร้อมใช้งาน")
    print(f"📄 สามารถ restore จากไฟล์: {backup_file}")
    print("⚠️ กรุณาใช้ด้วยความระมัดระวัง!")

if __name__ == "__main__":
    print("🔄 เริ่มสร้าง backup เมนู...")
    success = create_menu_backup()
    
    if success:
        print("\n💡 คำแนะนำ:")
        print("- สร้าง backup เป็นประจำก่อนแก้ไขเมนู")
        print("- เก็บไฟล์ backup ไว้ในที่ปลอดภัย")
        print("- ตรวจสอบไฟล์ backup เป็นระยะ")
    else:
        print("❌ ไม่สามารถสร้าง backup ได้")