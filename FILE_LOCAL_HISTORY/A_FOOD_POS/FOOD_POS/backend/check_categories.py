from .database import DatabaseManager
import os
import sqlite3

# ตรวจสอบไฟล์ฐานข้อมูลในโฟลเดอร์ A_FOOD_POS
db_path_main = "../pos_database.db"
print(f"Main database file path: {db_path_main}")
print(f"Main database file exists: {os.path.exists(db_path_main)}")

if os.path.exists(db_path_main):
    print(f"Main database file size: {os.path.getsize(db_path_main)} bytes")
    
    # เชื่อมต่อกับฐานข้อมูลหลัก
    conn = sqlite3.connect(db_path_main)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # ตรวจสอบจำนวนข้อมูลในตาราง menu_categories
    try:
        cursor.execute('SELECT COUNT(*) as count FROM menu_categories')
        count = cursor.fetchone()
        print(f"\nTotal categories in main database: {count['count']}")
        
        if count['count'] > 0:
            cursor.execute('SELECT category_id, name, is_active FROM menu_categories LIMIT 5')
            rows = cursor.fetchall()
            print('\nFirst 5 categories in main database:')
            for row in rows:
                print(f'ID: {row["category_id"]}, Name: {row["name"]}, Active: {row["is_active"]}')
    except Exception as e:
        print(f"\nError accessing main database: {e}")
    
    conn.close()

# ตรวจสอบไฟล์ฐานข้อมูลปัจจุบันที่ใช้โดย DatabaseManager
db = DatabaseManager()
print(f"\nCurrent database file path: {db.db_path}")
print(f"Current database file exists: {os.path.exists(db.db_path)}")
if os.path.exists(db.db_path):
    print(f"Current database file size: {os.path.getsize(db.db_path)} bytes")