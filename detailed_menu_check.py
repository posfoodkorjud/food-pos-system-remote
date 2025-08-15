import sqlite3
import os

# ตรวจสอบฐานข้อมูลปัจจุบันอย่างละเอียด
db_path = 'A_FOOD_POS/FOOD_POS/pos_database.db'
if not os.path.exists(db_path):
    db_path = 'A_FOOD_POS/pos_database.db'
    if not os.path.exists(db_path):
        print("ไม่พบไฟล์ฐานข้อมูล")
        exit(1)

print(f"ตรวจสอบฐานข้อมูล: {db_path}")
print("=" * 50)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ตรวจสอบหมวดหมู่ที่มีเมนูจริงๆ
    cursor.execute('''
        SELECT mc.name, COUNT(mi.item_id) as menu_count
        FROM menu_categories mc
        LEFT JOIN menu_items mi ON mc.category_id = mi.category_id AND mi.is_available = 1
        WHERE mc.is_active = 1
        GROUP BY mc.name
        HAVING COUNT(mi.item_id) > 0
        ORDER BY mc.name
    ''')
    active_categories = cursor.fetchall()
    
    print(f"หมวดหมู่ที่มีเมนู: {len(active_categories)} หมวด")
    total_menus = 0
    for cat_name, count in active_categories:
        print(f"- {cat_name}: {count} รายการ")
        total_menus += count
    
    print(f"\nรวมเมนูทั้งหมด: {total_menus} รายการ")
    
    # ตรวจสอบหมวดหมู่ที่ไม่มีเมนู
    cursor.execute('''
        SELECT mc.name
        FROM menu_categories mc
        LEFT JOIN menu_items mi ON mc.category_id = mi.category_id AND mi.is_available = 1
        WHERE mc.is_active = 1
        GROUP BY mc.name
        HAVING COUNT(mi.item_id) = 0
        ORDER BY mc.name
    ''')
    empty_categories = cursor.fetchall()
    
    if empty_categories:
        print(f"\nหมวดหมู่ที่ไม่มีเมนู: {len(empty_categories)} หมวด")
        for cat in empty_categories:
            print(f"- {cat[0]}")
    
    # แสดงตัวอย่างเมนูในแต่ละหมวด
    print("\n" + "=" * 50)
    print("ตัวอย่างเมนูในแต่ละหมวด:")
    for cat_name, count in active_categories:
        print(f"\n{cat_name} ({count} รายการ):")
        cursor.execute('''
            SELECT mi.name, mi.price
            FROM menu_items mi
            JOIN menu_categories mc ON mi.category_id = mc.category_id
            WHERE mc.name = ? AND mi.is_available = 1
            ORDER BY mi.name
            LIMIT 5
        ''', (cat_name,))
        sample_menus = cursor.fetchall()
        for menu_name, price in sample_menus:
            print(f"  - {menu_name} (฿{price})")
        if count > 5:
            print(f"  ... และอีก {count - 5} รายการ")
    
    conn.close()
    
except Exception as e:
    print(f'เกิดข้อผิดพลาด: {e}')