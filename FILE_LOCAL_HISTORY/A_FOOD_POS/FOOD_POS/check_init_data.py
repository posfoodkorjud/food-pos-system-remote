#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Database Initialization Script
สคริปต์ตรวจสอบการเริ่มต้นฐานข้อมูล
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

def check_init_data():
    """ตรวจสอบการเริ่มต้นฐานข้อมูล"""
    db = DatabaseManager()
    
    # ตรวจสอบว่ามีการเรียกใช้ init_default_data ทุกครั้งที่เริ่มต้นแอปหรือไม่
    print("\nChecking database initialization...")
    
    # ตรวจสอบโค้ดใน main.py ว่ามีการเรียกใช้ init_default_data หรือไม่
    try:
        with open(os.path.join(project_root, 'main.py'), 'r', encoding='utf-8') as f:
            main_content = f.read()
            if 'init_default_data' in main_content:
                print("✅ main.py calls init_default_data")
                print("\nThis might be causing duplicate categories each time the app starts!")
                print("The app might be adding default categories every time it starts.")
            else:
                print("❌ main.py does not call init_default_data directly")
    except Exception as e:
        print(f"Error reading main.py: {e}")
    
    # ตรวจสอบว่ามีการเรียกใช้ init_default_data จากที่อื่นหรือไม่
    try:
        with open(os.path.join(project_root, 'backend', 'database.py'), 'r', encoding='utf-8') as f:
            db_content = f.read()
            if 'init_default_data' in db_content and 'init_db' in db_content:
                print("\nChecking if init_default_data is called from init_db:")
                if 'init_default_data' in db_content.split('def init_db')[1].split('def')[0]:
                    print("✅ init_default_data is called from init_db")
                    print("\nThis might be causing duplicate categories when the database is initialized!")
                else:
                    print("❌ init_default_data is not called from init_db")
    except Exception as e:
        print(f"Error reading database.py: {e}")
    
    # ตรวจสอบหมวดหมู่ในฐานข้อมูล
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # ค้นหาหมวดหมู่ที่ซ้ำกัน
        cursor.execute("SELECT name, COUNT(*) FROM menu_categories GROUP BY name HAVING COUNT(*) > 1")
        duplicates = cursor.fetchall()
        
        if duplicates:
            print("\nDuplicate Categories Found:\n")
            print("Name | Count")
            print("-" * 20)
            
            for duplicate in duplicates:
                category_name = duplicate[0]
                count = duplicate[1]
                print(f"{category_name} | {count}")
                
                # ดึงรายการ ID ของหมวดหมู่ที่ซ้ำกัน
                cursor.execute("SELECT category_id, created_at FROM menu_categories WHERE name = ? ORDER BY category_id", (category_name,))
                categories = cursor.fetchall()
                
                print(f"  Category IDs and creation times:")
                for cat in categories:
                    print(f"  ID: {cat[0]}, Created: {cat[1]}")
        else:
            print("\nNo duplicate categories found.")
        
        # แสดงหมวดหมู่ทั้งหมด
        cursor.execute("SELECT * FROM menu_categories ORDER BY category_id")
        categories = cursor.fetchall()
        
        print("\nAll Categories:\n")
        print("ID | Name | Description | Is Active | Created At")
        print("-" * 70)
        
        for category in categories:
            print(f"{category[0]} | {category[1]} | {category[2]} | {category[3]} | {category[4]}")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดขณะตรวจสอบหมวดหมู่: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_init_data()