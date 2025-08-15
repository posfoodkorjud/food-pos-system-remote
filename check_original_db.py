import sqlite3
import os

# ตรวจสอบว่าไฟล์ฐานข้อมูลมีอยู่หรือไม่
db_path = 'FILE_LOCAL_HISTORY/A_FOOD_POS/FOOD_POS/pos_database.db'
if not os.path.exists(db_path):
    print(f"ไม่พบไฟล์ฐานข้อมูล: {db_path}")
    # ลองหาไฟล์ในตำแหน่งอื่น
    alternative_paths = [
        'FILE_LOCAL_HISTORY/A_FOOD_POS/pos_database.db',
        'FILE_LOCAL_HISTORY/pos_database.db',
        'A_FOOD_POS/FOOD_POS/pos_database.db',
        'A_FOOD_POS/pos_database.db'
    ]
    
    for alt_path in alternative_paths:
        if os.path.exists(alt_path):
            db_path = alt_path
            print(f"พบไฟล์ฐานข้อมูลที่: {db_path}")
            break
    else:
        print("ไม่พบไฟล์ฐานข้อมูลในตำแหน่งใดๆ")
        exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ตรวจสอบหมวดหมู่เมนู
    cursor.execute('SELECT COUNT(*) FROM menu_categories WHERE is_active = 1')
    category_count = cursor.fetchone()[0]
    print(f'หมวดหมู่เมนู: {category_count} รายการ')
    
    # ตรวจสอบรายการเมนู
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE is_available = 1')
    menu_count = cursor.fetchone()[0]
    print(f'รายการเมนู: {menu_count} รายการ')
    
    # แสดงรายชื่อหมวดหมู่
    cursor.execute('SELECT name FROM menu_categories WHERE is_active = 1 ORDER BY category_id')
    categories = cursor.fetchall()
    print('\nหมวดหมู่:')
    for cat in categories:
        print(f'- {cat[0]}')
    
    # ตรวจสอบจำนวนเมนูในแต่ละหมวด
    print('\nจำนวนเมนูในแต่ละหมวด:')
    cursor.execute('''
        SELECT mc.name, COUNT(mi.item_id) as menu_count
        FROM menu_categories mc
        LEFT JOIN menu_items mi ON mc.category_id = mi.category_id AND mi.is_available = 1
        WHERE mc.is_active = 1
        GROUP BY mc.category_id, mc.name
        ORDER BY mc.category_id
    ''')
    category_stats = cursor.fetchall()
    for cat_name, count in category_stats:
        print(f'- {cat_name}: {count} รายการ')
    
    conn.close()
    print(f'\nตรวจสอบฐานข้อมูลเสร็จสิ้น: {db_path}')
    
except Exception as e:
    print(f'เกิดข้อผิดพลาด: {e}')