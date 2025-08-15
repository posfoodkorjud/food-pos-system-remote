#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Database Script
สคริปต์แก้ไขฐานข้อมูลให้มี 4 หมวดหมู่และ 77 เมนู
"""

import sqlite3
import sys
from pathlib import Path

def fix_database():
    """แก้ไขฐานข้อมูลให้ถูกต้อง"""
    db_path = "pos_database.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== ตรวจสอบสถานะปัจจุบัน ===")
        
        # นับจำนวนหมวดหมู่
        cursor.execute("SELECT COUNT(*) FROM menu_categories WHERE is_active = 1")
        category_count = cursor.fetchone()[0]
        print(f"จำนวนหมวดหมู่ปัจจุบัน: {category_count}")
        
        # นับจำนวนเมนู
        cursor.execute("SELECT COUNT(*) FROM menu_items WHERE is_available = 1")
        menu_count = cursor.fetchone()[0]
        print(f"จำนวนเมนูปัจจุบัน: {menu_count}")
        
        print("\n=== เริ่มแก้ไขฐานข้อมูล ===")
        
        # 1. ลบหมวดหมู่ที่ซ้ำกัน - เก็บเฉพาะ ID ที่เล็กที่สุดของแต่ละหมวดหมู่
        print("1. กำลังลบหมวดหมู่ที่ซ้ำกัน...")
        
        # หาหมวดหมู่ที่ซ้ำกันและลบที่มี ID สูงกว่า
        cursor.execute("""
            DELETE FROM menu_categories 
            WHERE category_id NOT IN (
                SELECT MIN(category_id) 
                FROM menu_categories 
                GROUP BY name
            )
        """)
        
        # อัปเดตเมนูที่อ้างอิงหมวดหมู่ที่ถูกลบ
        cursor.execute("""
            UPDATE menu_items 
            SET category_id = (
                SELECT MIN(category_id) 
                FROM menu_categories 
                WHERE menu_categories.name = (
                    SELECT name FROM menu_categories mc2 
                    WHERE mc2.category_id = menu_items.category_id
                    LIMIT 1
                )
            )
            WHERE category_id NOT IN (
                SELECT category_id FROM menu_categories
            )
        """)
        
        # 2. ตรวจสอบและลบหมวดหมู่ที่เกิน 4 หมวดหมู่
        cursor.execute("SELECT COUNT(*) FROM menu_categories WHERE is_active = 1")
        remaining_categories = cursor.fetchone()[0]
        
        if remaining_categories > 4:
            print(f"2. กำลังลบหมวดหมู่ที่เกิน (เหลือ {remaining_categories} หมวดหมู่)...")
            
            # เก็บเฉพาะ 4 หมวดหมู่แรก
            cursor.execute("""
                UPDATE menu_categories 
                SET is_active = 0 
                WHERE category_id NOT IN (
                    SELECT category_id 
                    FROM menu_categories 
                    WHERE is_active = 1 
                    ORDER BY category_id 
                    LIMIT 4
                )
            """)
            
            # ปิดการใช้งานเมนูที่อยู่ในหมวดหมู่ที่ถูกปิด
            cursor.execute("""
                UPDATE menu_items 
                SET is_available = 0 
                WHERE category_id IN (
                    SELECT category_id 
                    FROM menu_categories 
                    WHERE is_active = 0
                )
            """)
        
        # 3. ตรวจสอบและลบเมนูที่เกิน 77 เมนู
        cursor.execute("SELECT COUNT(*) FROM menu_items WHERE is_available = 1")
        remaining_menus = cursor.fetchone()[0]
        
        if remaining_menus > 77:
            print(f"3. กำลังลบเมนูที่เกิน (เหลือ {remaining_menus} เมนู)...")
            
            # เก็บเฉพาะ 77 เมนูแรก
            cursor.execute("""
                UPDATE menu_items 
                SET is_available = 0 
                WHERE item_id NOT IN (
                    SELECT item_id 
                    FROM menu_items 
                    WHERE is_available = 1 
                    ORDER BY item_id 
                    LIMIT 77
                )
            """)
        
        # บันทึกการเปลี่ยนแปลง
        conn.commit()
        
        print("\n=== ตรวจสอบผลลัพธ์ ===")
        
        # ตรวจสอบผลลัพธ์
        cursor.execute("SELECT COUNT(*) FROM menu_categories WHERE is_active = 1")
        final_category_count = cursor.fetchone()[0]
        print(f"จำนวนหมวดหมู่หลังแก้ไข: {final_category_count}")
        
        cursor.execute("SELECT COUNT(*) FROM menu_items WHERE is_available = 1")
        final_menu_count = cursor.fetchone()[0]
        print(f"จำนวนเมนูหลังแก้ไข: {final_menu_count}")
        
        # แสดงหมวดหมู่ที่เหลือ
        cursor.execute("SELECT category_id, name FROM menu_categories WHERE is_active = 1 ORDER BY category_id")
        categories = cursor.fetchall()
        print("\nหมวดหมู่ที่เหลือ:")
        for cat in categories:
            print(f"  - ID: {cat[0]}, Name: {cat[1]}")
        
        conn.close()
        
        print("\n✅ แก้ไขฐานข้อมูลเสร็จสิ้น!")
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    fix_database()