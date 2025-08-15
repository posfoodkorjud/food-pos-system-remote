#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Categories Script
สคริปต์ตรวจสอบหมวดหมู่ในฐานข้อมูล
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

def check_categories():
    """ตรวจสอบหมวดหมู่ในฐานข้อมูล"""
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # ดึงข้อมูลหมวดหมู่ทั้งหมด
        cursor.execute("SELECT * FROM menu_categories")
        categories = cursor.fetchall()
        
        print("\nMenu Categories:\n")
        print("ID | Name | Description | Is Active")
        print("-" * 50)
        
        for category in categories:
            print(f"{category[0]} | {category[1]} | {category[2]} | {category[3]}")
        
        # นับจำนวนหมวดหมู่ที่ซ้ำกัน
        cursor.execute("SELECT name, COUNT(*) FROM menu_categories GROUP BY name HAVING COUNT(*) > 1")
        duplicates = cursor.fetchall()
        
        if duplicates:
            print("\nDuplicate Categories:\n")
            print("Name | Count")
            print("-" * 20)
            
            for duplicate in duplicates:
                print(f"{duplicate[0]} | {duplicate[1]}")
                
                # แสดงรายละเอียดของหมวดหมู่ที่ซ้ำกัน
                cursor.execute("SELECT * FROM menu_categories WHERE name = ?", (duplicate[0],))
                details = cursor.fetchall()
                
                print("\nDetails:")
                for detail in details:
                    print(f"ID: {detail[0]}, Name: {detail[1]}, Description: {detail[2]}, Is Active: {detail[3]}")
        else:
            print("\nNo duplicate categories found.")
        
        return True
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดขณะตรวจสอบหมวดหมู่: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_categories()