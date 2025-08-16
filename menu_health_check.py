#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับตรวจสอบความถูกต้องของเมนู POS
ใช้สำหรับตรวจสอบปัญหาต่างๆ ที่อาจเกิดขึ้นกับเมนู
"""

import sqlite3
import os
from datetime import datetime
from collections import Counter

def check_menu_health():
    """ตรวจสอบความถูกต้องของเมนูทั้งหมด"""
    
    db_path = "A_FOOD_POS/FOOD_POS/pos_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบไฟล์ฐานข้อมูล: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 เริ่มตรวจสอบความถูกต้องของเมนู...")
        print("="*60)
        
        issues_found = []
        
        # 1. ตรวจสอบจำนวนหมวดหมู่
        cursor.execute("SELECT COUNT(*) FROM menu_categories WHERE is_active = 1")
        category_count = cursor.fetchone()[0]
        
        print(f"📂 จำนวนหมวดหมู่ที่ใช้งาน: {category_count}")
        
        if category_count != 4:
            issues_found.append(f"⚠️ จำนวนหมวดหมู่ไม่ถูกต้อง: {category_count} (ควรเป็น 4)")
        
        # 2. ตรวจสอบจำนวนเมนู
        cursor.execute("SELECT COUNT(*) FROM menu_items WHERE is_available = 1")
        menu_count = cursor.fetchone()[0]
        
        print(f"🍽️ จำนวนเมนูที่พร้อมขาย: {menu_count}")
        
        if menu_count != 77:
            issues_found.append(f"⚠️ จำนวนเมนูไม่ถูกต้อง: {menu_count} (ควรเป็น 77)")
        
        # 3. ตรวจสอบช่วงราคา
        cursor.execute("SELECT MIN(price), MAX(price) FROM menu_items WHERE is_available = 1")
        min_price, max_price = cursor.fetchone()
        
        print(f"💰 ช่วงราคา: {min_price}-{max_price} บาท")
        
        if min_price < 15 or max_price > 59:
            issues_found.append(f"⚠️ ราคาเมนูอยู่นอกช่วงที่กำหนด: {min_price}-{max_price} (ควรเป็น 15-59)")
        
        # 4. ตรวจสอบเมนูที่มีชื่อซ้ำ
        cursor.execute("SELECT name, COUNT(*) FROM menu_items WHERE is_available = 1 GROUP BY name HAVING COUNT(*) > 1")
        duplicate_names = cursor.fetchall()
        
        if duplicate_names:
            print(f"❌ พบเมนูที่มีชื่อซ้ำ: {len(duplicate_names)} รายการ")
            for name, count in duplicate_names:
                print(f"  - '{name}': {count} รายการ")
                issues_found.append(f"⚠️ เมนูชื่อซ้ำ: {name} ({count} รายการ)")
        else:
            print("✅ ไม่พบเมนูที่มีชื่อซ้ำ")
        
        # 5. ตรวจสอบหมวดหมู่ที่มีชื่อซ้ำ
        cursor.execute("SELECT name, COUNT(*) FROM menu_categories WHERE is_active = 1 GROUP BY name HAVING COUNT(*) > 1")
        duplicate_categories = cursor.fetchall()
        
        if duplicate_categories:
            print(f"❌ พบหมวดหมู่ที่มีชื่อซ้ำ: {len(duplicate_categories)} รายการ")
            for name, count in duplicate_categories:
                print(f"  - '{name}': {count} รายการ")
                issues_found.append(f"⚠️ หมวดหมู่ชื่อซ้ำ: {name} ({count} รายการ)")
        else:
            print("✅ ไม่พบหมวดหมู่ที่มีชื่อซ้ำ")
        
        # 6. ตรวจสอบเมนูที่ไม่มีหมวดหมู่
        cursor.execute("""
            SELECT m.name, m.category_id 
            FROM menu_items m 
            LEFT JOIN menu_categories c ON m.category_id = c.category_id 
            WHERE m.is_available = 1 AND (c.category_id IS NULL OR c.is_active = 0)
        """)
        orphan_items = cursor.fetchall()
        
        if orphan_items:
            print(f"❌ พบเมนูที่ไม่มีหมวดหมู่หรือหมวดหมู่ไม่ใช้งาน: {len(orphan_items)} รายการ")
            for name, category_id in orphan_items:
                print(f"  - '{name}' (category_id: {category_id})")
                issues_found.append(f"⚠️ เมนูไม่มีหมวดหมู่: {name}")
        else:
            print("✅ เมนูทุกรายการมีหมวดหมู่ที่ถูกต้อง")
        
        # 7. ตรวจสอบการกระจายเมนูในแต่ละหมวดหมู่
        cursor.execute("""
            SELECT c.name, COUNT(m.item_id) as item_count
            FROM menu_categories c
            LEFT JOIN menu_items m ON c.category_id = m.category_id AND m.is_available = 1
            WHERE c.is_active = 1
            GROUP BY c.category_id, c.name
            ORDER BY c.name
        """)
        category_distribution = cursor.fetchall()
        
        print(f"\n📊 การกระจายเมนูในแต่ละหมวดหมู่:")
        for cat_name, item_count in category_distribution:
            print(f"  - {cat_name}: {item_count} รายการ")
            
            # ตรวจสอบหมวดหมู่ที่ไม่มีเมนู
            if item_count == 0:
                issues_found.append(f"⚠️ หมวดหมู่ '{cat_name}' ไม่มีเมนู")
        
        # 8. ตรวจสอบเมนูที่มีราคาผิดปกติ
        cursor.execute("SELECT name, price FROM menu_items WHERE is_available = 1 AND (price <= 0 OR price IS NULL)")
        invalid_prices = cursor.fetchall()
        
        if invalid_prices:
            print(f"❌ พบเมนูที่มีราคาผิดปกติ: {len(invalid_prices)} รายการ")
            for name, price in invalid_prices:
                print(f"  - '{name}': {price} บาท")
                issues_found.append(f"⚠️ เมนูราคาผิดปกติ: {name} ({price})")
        else:
            print("✅ ราคาเมนูทุกรายการถูกต้อง")
        
        conn.close()
        
        # สรุปผลการตรวจสอบ
        print("\n" + "="*60)
        
        if not issues_found:
            print("🎉 ไม่พบปัญหาใดๆ เมนูอยู่ในสภาพที่ดี!")
            print(f"✅ หมวดหมู่: {category_count} รายการ")
            print(f"✅ เมนู: {menu_count} รายการ")
            print(f"✅ ช่วงราคา: {min_price}-{max_price} บาท")
            return True
        else:
            print(f"⚠️ พบปัญหา {len(issues_found)} รายการ:")
            for i, issue in enumerate(issues_found, 1):
                print(f"  {i}. {issue}")
            
            print("\n💡 คำแนะนำ:")
            print("- ตรวจสอบและแก้ไขปัญหาที่พบ")
            print("- สร้าง backup ก่อนแก้ไข")
            print("- รันการตรวจสอบอีกครั้งหลังแก้ไข")
            return False
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการตรวจสอบ: {e}")
        return False

def generate_menu_report():
    """สร้างรายงานสถานะเมนูแบบละเอียด"""
    
    db_path = "A_FOOD_POS/FOOD_POS/pos_database.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # สร้างไฟล์รายงาน
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"menu_health_report_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"=== รายงานสถานะเมนู POS ===\n")
            f.write(f"วันที่สร้างรายงาน: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # ข้อมูลทั่วไป
            cursor.execute("SELECT COUNT(*) FROM menu_categories WHERE is_active = 1")
            category_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM menu_items WHERE is_available = 1")
            menu_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(price), MAX(price), AVG(price) FROM menu_items WHERE is_available = 1")
            min_price, max_price, avg_price = cursor.fetchone()
            
            f.write(f"📊 สรุปข้อมูลทั่วไป:\n")
            f.write(f"- จำนวนหมวดหมู่: {category_count}\n")
            f.write(f"- จำนวนเมนู: {menu_count}\n")
            f.write(f"- ช่วงราคา: {min_price}-{max_price} บาท\n")
            f.write(f"- ราคาเฉลี่ย: {avg_price:.2f} บาท\n\n")
            
            # รายละเอียดแต่ละหมวดหมู่
            cursor.execute("""
                SELECT c.name, COUNT(m.item_id) as item_count,
                       MIN(m.price) as min_price, MAX(m.price) as max_price
                FROM menu_categories c
                LEFT JOIN menu_items m ON c.category_id = m.category_id AND m.is_available = 1
                WHERE c.is_active = 1
                GROUP BY c.category_id, c.name
                ORDER BY c.name
            """)
            categories = cursor.fetchall()
            
            f.write(f"📂 รายละเอียดแต่ละหมวดหมู่:\n")
            for cat_name, item_count, min_price, max_price in categories:
                f.write(f"\n{cat_name}:\n")
                f.write(f"  - จำนวนเมนู: {item_count}\n")
                if item_count > 0:
                    f.write(f"  - ช่วงราคา: {min_price}-{max_price} บาท\n")
                
                # รายการเมนูในหมวดหมู่
                cursor.execute("""
                    SELECT m.name, m.price
                    FROM menu_items m
                    JOIN menu_categories c ON m.category_id = c.category_id
                    WHERE c.name = ? AND m.is_available = 1 AND c.is_active = 1
                    ORDER BY m.name
                """, (cat_name,))
                items = cursor.fetchall()
                
                for item_name, price in items:
                    f.write(f"    • {item_name}: {price} บาท\n")
        
        conn.close()
        
        print(f"✅ สร้างรายงานเรียบร้อย: {report_file}")
        return report_file
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้างรายงาน: {e}")
        return None

if __name__ == "__main__":
    print("🏥 เครื่องมือตรวจสอบสุขภาพเมนู POS")
    print("="*50)
    
    # ตรวจสอบความถูกต้อง
    health_status = check_menu_health()
    
    # เสนอให้สร้างรายงาน
    if health_status:
        create_report = input("\n📄 ต้องการสร้างรายงานแบบละเอียดหรือไม่? (y/n): ").lower().strip()
        if create_report == 'y':
            generate_menu_report()
    
    print("\n💡 คำแนะนำ:")
    print("- รันการตรวจสอบนี้เป็นประจำ")
    print("- สร้าง backup ก่อนแก้ไขเมนู")
    print("- ตรวจสอบหลังจากแก้ไขเมนูทุกครั้ง")