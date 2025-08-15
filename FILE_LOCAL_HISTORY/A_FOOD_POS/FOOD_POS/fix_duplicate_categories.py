#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Duplicate Categories Script
สคริปต์แก้ไขหมวดหมู่ที่ซ้ำกัน
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

def fix_duplicate_categories():
    """แก้ไขหมวดหมู่ที่ซ้ำกัน"""
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # ค้นหาหมวดหมู่ที่ซ้ำกัน
        cursor.execute("SELECT name, COUNT(*) FROM menu_categories GROUP BY name HAVING COUNT(*) > 1")
        duplicates = cursor.fetchall()
        
        if not duplicates:
            print("\nNo duplicate categories found.")
            return True
        
        print("\nDuplicate Categories Found:\n")
        print("Name | Count")
        print("-" * 20)
        
        for duplicate in duplicates:
            category_name = duplicate[0]
            count = duplicate[1]
            print(f"{category_name} | {count}")
            
            # ดึงรายการ ID ของหมวดหมู่ที่ซ้ำกัน
            cursor.execute("SELECT category_id FROM menu_categories WHERE name = ? ORDER BY category_id", (category_name,))
            category_ids = [row[0] for row in cursor.fetchall()]
            
            # เก็บ ID แรกไว้ และลบที่เหลือ
            keep_id = category_ids[0]
            delete_ids = category_ids[1:]
            
            print(f"  Keeping category ID: {keep_id}")
            print(f"  Deleting category IDs: {delete_ids}")
            
            # อัปเดตรายการเมนูที่อ้างอิงถึงหมวดหมู่ที่จะลบ ให้อ้างอิงถึงหมวดหมู่ที่จะเก็บไว้แทน
            for delete_id in delete_ids:
                cursor.execute("UPDATE menu_items SET category_id = ? WHERE category_id = ?", (keep_id, delete_id))
                print(f"  Updated menu items from category ID {delete_id} to {keep_id}")
                
                # ลบหมวดหมู่ที่ซ้ำกัน
                cursor.execute("DELETE FROM menu_categories WHERE category_id = ?", (delete_id,))
                print(f"  Deleted category ID: {delete_id}")
        
        conn.commit()
        print("\n✅ Fixed all duplicate categories successfully!")
        
        # แสดงหมวดหมู่ที่เหลือ
        cursor.execute("SELECT * FROM menu_categories ORDER BY category_id")
        categories = cursor.fetchall()
        
        print("\nRemaining Categories:\n")
        print("ID | Name | Description | Is Active")
        print("-" * 50)
        
        for category in categories:
            print(f"{category[0]} | {category[1]} | {category[2]} | {category[3]}")
        
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ เกิดข้อผิดพลาดขณะแก้ไขหมวดหมู่ที่ซ้ำกัน: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_duplicate_categories()