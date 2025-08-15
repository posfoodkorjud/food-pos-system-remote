#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Consistency Checker
ตรวจสอบความสอดคล้องของชื่อคอลัมน์ในฐานข้อมูลและโค้ด
"""

import sqlite3
import os
import re
from pathlib import Path

def check_database_schema():
    """ตรวจสอบโครงสร้างฐานข้อมูล"""
    print("=== ตรวจสอบโครงสร้างฐานข้อมูล ===")
    
    try:
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ตรวจสอบตาราง order_items
        cursor.execute('PRAGMA table_info(order_items)')
        columns = cursor.fetchall()
        
        print("\nคอลัมน์ในตาราง order_items:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # ตรวจสอบว่ามี customer_request หรือ special_request
        column_names = [col[1] for col in columns]
        
        if 'customer_request' in column_names:
            print("✅ พบคอลัมน์ 'customer_request' ในฐานข้อมูล")
        else:
            print("❌ ไม่พบคอลัมน์ 'customer_request' ในฐานข้อมูล")
            
        if 'special_request' in column_names:
            print("⚠️  พบคอลัมน์ 'special_request' ในฐานข้อมูล (ควรเปลี่ยนเป็น customer_request)")
        
        conn.close()
        return column_names
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return []

def check_code_consistency():
    """ตรวจสอบความสอดคล้องในโค้ด"""
    print("\n=== ตรวจสอบความสอดคล้องในโค้ด ===")
    
    # ไฟล์ที่ต้องตรวจสอบ
    files_to_check = [
        'backend/app.py',
        'backend/database.py',
        'backend/admin.js'
    ]
    
    issues = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\nตรวจสอบไฟล์: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # ค้นหา special_request
            special_request_matches = re.findall(r'special_request', content)
            customer_request_matches = re.findall(r'customer_request', content)
            
            if special_request_matches:
                print(f"  ⚠️  พบ 'special_request' {len(special_request_matches)} ครั้ง")
                issues.append(f"{file_path}: พบ special_request {len(special_request_matches)} ครั้ง")
            
            if customer_request_matches:
                print(f"  ✅ พบ 'customer_request' {len(customer_request_matches)} ครั้ง")
        else:
            print(f"  ❌ ไม่พบไฟล์: {file_path}")
    
    return issues

def generate_fix_script(issues):
    """สร้างสคริปต์แก้ไขอัตโนมัติ"""
    if not issues:
        print("\n✅ ไม่พบปัญหาความสอดคล้อง")
        return
    
    print("\n=== สร้างสคริปต์แก้ไข ===")
    
    fix_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-fix script for special_request -> customer_request
"""

import re
import os

def fix_file(file_path):
    """แก้ไขไฟล์โดยเปลี่ยน special_request เป็น customer_request"""
    if not os.path.exists(file_path):
        print(f"ไม่พบไฟล์: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # สำรองไฟล์เดิม
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # แทนที่ special_request ด้วย customer_request
        new_content = content.replace('special_request', 'customer_request')
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ แก้ไขไฟล์: {file_path}")
            return True
        else:
            print(f"ไม่มีการเปลี่ยนแปลงใน: {file_path}")
            os.remove(backup_path)  # ลบไฟล์สำรอง
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการแก้ไข {file_path}: {e}")
        return False

if __name__ == "__main__":
    files_to_fix = [
        'backend/app.py',
        'backend/database.py',
        'backend/admin.js'
    ]
    
    print("🔧 เริ่มแก้ไขไฟล์...")
    
    for file_path in files_to_fix:
        fix_file(file_path)
    
    print("\n✅ เสร็จสิ้นการแก้ไข")
    print("📝 ไฟล์สำรองถูกสร้างด้วยนามสกุล .backup")
'''
    
    with open('fix_special_request.py', 'w', encoding='utf-8') as f:
        f.write(fix_script)
    
    print("✅ สร้างไฟล์ fix_special_request.py เรียบร้อย")

def main():
    """ฟังก์ชันหลัก"""
    print("🔍 Database Consistency Checker")
    print("ตรวจสอบความสอดคล้องของ special_request/customer_request")
    print("=" * 60)
    
    # ตรวจสอบฐานข้อมูล
    db_columns = check_database_schema()
    
    # ตรวจสอบโค้ด
    code_issues = check_code_consistency()
    
    # สร้างสคริปต์แก้ไข
    generate_fix_script(code_issues)
    
    print("\n=== สรุปผลการตรวจสอบ ===")
    if not code_issues:
        print("✅ ระบบมีความสอดคล้องแล้ว")
    else:
        print("⚠️  พบปัญหาความสอดคล้อง:")
        for issue in code_issues:
            print(f"  - {issue}")
        print("\n💡 แนะนำ: รันไฟล์ fix_special_request.py เพื่อแก้ไขอัตโนมัติ")

if __name__ == "__main__":
    main()