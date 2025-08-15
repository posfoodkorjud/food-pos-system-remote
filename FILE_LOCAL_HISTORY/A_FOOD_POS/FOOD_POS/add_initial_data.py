#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add Initial Data Script
สคริปต์เพิ่มข้อมูลเริ่มต้นสำหรับระบบ POS
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))

try:
    from database import DatabaseManager
except ImportError as e:
    print(f"Error importing DatabaseManager: {e}")
    # Try alternative import
    try:
        sys.path.insert(0, str(project_root))
        from backend.database import DatabaseManager
    except ImportError as e2:
        print(f"Alternative import also failed: {e2}")
        sys.exit(1)

def add_initial_data():
    """เพิ่มข้อมูลเริ่มต้นลงในฐานข้อมูล"""
    print("Adding initial data to database...")
    
    try:
        db = DatabaseManager()
        
        # ตรวจสอบว่ามีข้อมูลอยู่แล้วหรือไม่
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # ตรวจสอบจำนวนหมวดหมู่
        cursor.execute("SELECT COUNT(*) FROM menu_categories")
        category_count = cursor.fetchone()[0]
        
        # ตรวจสอบจำนวนเมนู
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        menu_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"Current categories: {category_count}")
        print(f"Current menu items: {menu_count}")
        
        if category_count > 0 or menu_count > 0:
            response = input("Data already exists. Do you want to add more data? (y/n): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return
        
        # เรียกใช้ฟังก์ชันเพิ่มข้อมูลเริ่มต้น
        db.init_default_data()
        
        # ตรวจสอบผลลัพธ์
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM menu_categories")
        new_category_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        new_menu_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tables")
        table_count = cursor.fetchone()[0]
        
        conn.close()
        
        print("\n=== Initial Data Added Successfully! ===")
        print(f"Categories: {new_category_count}")
        print(f"Menu items: {new_menu_count}")
        print(f"Tables: {table_count}")
        
        # แสดงหมวดหมู่ที่เพิ่ม
        print("\n=== Categories Added ===")
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT category_id, name, description FROM menu_categories ORDER BY category_id")
        categories = cursor.fetchall()
        
        for cat in categories:
            print(f"ID: {cat[0]}, Name: {cat[1]}, Description: {cat[2]}")
        
        # แสดงเมนูที่เพิ่ม
        print("\n=== Menu Items Added ===")
        cursor.execute("SELECT item_id, name, price, category_id FROM menu_items ORDER BY item_id")
        items = cursor.fetchall()
        
        for item in items:
            print(f"ID: {item[0]}, Name: {item[1]}, Price: {item[2]}, Category: {item[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error adding initial data: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = add_initial_data()
    if success:
        print("\n✅ Initial data added successfully!")
        print("You can now use the POS system with sample menu items.")
    else:
        print("\n❌ Failed to add initial data.")
        sys.exit(1)