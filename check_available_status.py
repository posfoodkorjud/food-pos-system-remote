import sqlite3
import os

# ตรวจสอบสถานะ is_available ของเมนูอย่างละเอียด
db_path = 'A_FOOD_POS/FOOD_POS/pos_database.db'
if not os.path.exists(db_path):
    db_path = 'A_FOOD_POS/pos_database.db'
    if not os.path.exists(db_path):
        print("ไม่พบไฟล์ฐานข้อมูล")
        exit(1)

print(f"ตรวจสอบฐานข้อมูล: {db_path}")
print("=" * 60)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ตรวจสอบจำนวนเมนูทั้งหมดแยกตามสถานะ
    cursor.execute('SELECT COUNT(*) FROM menu_items')
    total_items = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE is_available = 1')
    available_items = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE is_available = 0')
    unavailable_items = cursor.fetchone()[0]
    
    print(f"สรุปจำนวนเมนู:")
    print(f"- เมนูทั้งหมด: {total_items} รายการ")
    print(f"- เมนูที่พร้อมจำหน่าย (is_available = 1): {available_items} รายการ")
    print(f"- เมนูที่ไม่พร้อมจำหน่าย (is_available = 0): {unavailable_items} รายการ")
    
    # แสดงเมนูที่ไม่พร้อมจำหน่าย
    if unavailable_items > 0:
        print(f"\nรายการเมนูที่ไม่พร้อมจำหน่าย ({unavailable_items} รายการ):")
        cursor.execute('''
            SELECT mi.name, mc.name as category, mi.price
            FROM menu_items mi
            JOIN menu_categories mc ON mi.category_id = mc.category_id
            WHERE mi.is_available = 0
            ORDER BY mc.name, mi.name
        ''')
        unavailable_menus = cursor.fetchall()
        
        current_category = None
        for menu_name, category, price in unavailable_menus:
            if category != current_category:
                print(f"\n[{category}]")
                current_category = category
            print(f"  - {menu_name} (฿{price})")
    
    # ตรวจสอบหมวดหมู่ที่มีเมนูพร้อมจำหน่าย
    print(f"\n" + "=" * 60)
    print(f"หมวดหมู่ที่มีเมนูพร้อมจำหน่าย:")
    cursor.execute('''
        SELECT mc.name, COUNT(mi.item_id) as available_count
        FROM menu_categories mc
        LEFT JOIN menu_items mi ON mc.category_id = mi.category_id AND mi.is_available = 1
        WHERE mc.is_active = 1
        GROUP BY mc.name
        HAVING COUNT(mi.item_id) > 0
        ORDER BY mc.name
    ''')
    available_categories = cursor.fetchall()
    
    total_available = 0
    for cat_name, count in available_categories:
        print(f"- {cat_name}: {count} รายการ")
        total_available += count
    
    print(f"\nรวมเมนูที่พร้อมจำหน่าย: {total_available} รายการ")
    
    # ตรวจสอบว่าตรงกับ 77 รายการหรือไม่
    if total_available == 77:
        print("\n✅ ตรงกับจำนวน 77 รายการที่คุณระบุ!")
    else:
        print(f"\n❌ ไม่ตรงกับ 77 รายการ (ต่างกัน {abs(total_available - 77)} รายการ)")
    
    conn.close()
    
except Exception as e:
    print(f'เกิดข้อผิดพลาด: {e}')