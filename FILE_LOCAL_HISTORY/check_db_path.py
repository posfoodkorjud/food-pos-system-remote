#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import sqlite3
sys.path.append(os.path.join(os.path.dirname(__file__), 'A_FOOD_POS', 'FOOD_POS', 'backend'))

from database import DatabaseManager

def check_database_paths():
    """ตรวจสอบว่า DatabaseManager เชื่อมต่อกับฐานข้อมูลไฟล์ไหน"""
    
    print("=== ตรวจสอบ Database Paths ===")
    
    # ตรวจสอบไฟล์ฐานข้อมูลต่างๆ
    db_files = [
        'pos_database.db',
        'A_FOOD_POS/FOOD_POS/pos_database.db',
        'A_FOOD_POS/FOOD_POS/data/food_pos.db',
        '../pos_database.db'
    ]
    
    for db_file in db_files:
        full_path = os.path.abspath(db_file)
        exists = os.path.exists(full_path)
        
        if exists:
            print(f"\n=== ตรวจสอบ {db_file} ===")
            print(f"Path: {full_path}")
            
            try:
                conn = sqlite3.connect(db_file)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # นับจำนวนออเดอร์
                cursor.execute("SELECT COUNT(*) as count FROM orders WHERE DATE(created_at) BETWEEN '2025-08-05' AND '2025-08-11'")
                count_result = cursor.fetchone()
                order_count = count_result['count'] if count_result else 0
                
                # คำนวณยอดขาย
                cursor.execute("""
                    SELECT SUM(total_amount) as total 
                    FROM orders 
                    WHERE DATE(created_at) BETWEEN '2025-08-05' AND '2025-08-11' 
                    AND status != 'rejected'
                """)
                total_result = cursor.fetchone()
                total_sales = total_result['total'] if total_result and total_result['total'] else 0
                
                print(f"  จำนวนออเดอร์: {order_count}")
                print(f"  ยอดขายรวม: {total_sales} บาท")
                
                conn.close()
                
            except Exception as e:
                print(f"  ❌ เกิดข้อผิดพลาด: {e}")
        else:
            print(f"\n❌ ไม่พบไฟล์: {db_file}")
    
    # ตรวจสอบ DatabaseManager
    print("\n=== ตรวจสอบ DatabaseManager ===")
    
    try:
        db = DatabaseManager()
        print(f"DatabaseManager db_path: {getattr(db, 'db_path', 'ไม่พบ')}")
        
        # ตรวจสอบ connection
        conn = db.get_connection()
        print(f"Connection object: {conn}")
        
        # ตรวจสอบ path ที่แท้จริงของ connection
        cursor = conn.cursor()
        cursor.execute("PRAGMA database_list")
        db_list = cursor.fetchall()
        
        print("Database list:")
        for db_info in db_list:
            print(f"  {db_info}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดกับ DatabaseManager: {e}")
        import traceback
        traceback.print_exc()
    
    # ตรวจสอบ working directory
    print(f"\n=== Working Directory ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {os.path.dirname(__file__)}")
    
    # ตรวจสอบ backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'A_FOOD_POS', 'FOOD_POS', 'backend')
    print(f"Backend directory: {os.path.abspath(backend_dir)}")
    print(f"Backend exists: {os.path.exists(backend_dir)}")
    
    if os.path.exists(backend_dir):
        backend_db = os.path.join(backend_dir, 'pos_database.db')
        print(f"Backend DB: {backend_db}")
        print(f"Backend DB exists: {os.path.exists(backend_db)}")

if __name__ == '__main__':
    check_database_paths()