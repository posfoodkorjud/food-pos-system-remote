import sqlite3
import os

# ตรวจสอบฐานข้อมูลปัจจุบัน
db_paths = [
    'A_FOOD_POS/FOOD_POS/pos_database.db',
    'A_FOOD_POS/pos_database.db',
    'pos_database.db'
]

db_path = None
for path in db_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("ไม่พบไฟล์ฐานข้อมูลปัจจุบัน")
    exit(1)

print(f"ตรวจสอบฐานข้อมูลปัจจุบัน: {db_path}")

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
    
    # แสดงรายชื่อหมวดหมู่ที่ไม่ซ้ำ
    cursor.execute('SELECT DISTINCT name FROM menu_categories WHERE is_active = 1 ORDER BY name')
    categories = cursor.fetchall()
    print(f'\nหมวดหมู่ที่ไม่ซ้ำ ({len(categories)} หมวด):')
    for cat in categories:
        print(f'- {cat[0]}')
    
    # ตรวจสอบจำนวนเมนูในแต่ละหมวด (ไม่ซ้ำ)
    print('\nจำนวนเมนูในแต่ละหมวด:')
    cursor.execute('''
        SELECT mc.name, COUNT(DISTINCT mi.item_id) as menu_count
        FROM menu_categories mc
        LEFT JOIN menu_items mi ON mc.category_id = mi.category_id AND mi.is_available = 1
        WHERE mc.is_active = 1
        GROUP BY mc.name
        ORDER BY mc.name
    ''')
    category_stats = cursor.fetchall()
    total_unique_menus = 0
    for cat_name, count in category_stats:
        print(f'- {cat_name}: {count} รายการ')
        total_unique_menus += count
    
    print(f'\nรวมเมนูทั้งหมด: {total_unique_menus} รายการ')
    
    # ตรวจสอบข้อมูลซ้ำ
    cursor.execute('SELECT COUNT(*) FROM menu_categories')
    total_categories = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(DISTINCT name) FROM menu_categories WHERE is_active = 1')
    unique_categories = cursor.fetchone()[0]
    
    print(f'\nสถิติหมวดหมู่:')
    print(f'- หมวดหมู่ทั้งหมด: {total_categories}')
    print(f'- หมวดหมู่ที่ active: {category_count}')
    print(f'- หมวดหมู่ที่ไม่ซ้ำ: {unique_categories}')
    
    conn.close()
    
except Exception as e:
    print(f'เกิดข้อผิดพลาด: {e}')