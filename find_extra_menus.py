import sqlite3
import os

# หาเมนูที่อาจจะเป็นรายการเพิ่มเติมที่ไม่ต้องการ
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
    
    # แสดงเมนูทั้งหมดแยกตามหมวดหมู่
    cursor.execute('''
        SELECT mc.name as category, mi.name, mi.price, mi.item_id, mi.created_at
        FROM menu_items mi
        JOIN menu_categories mc ON mi.category_id = mc.category_id
        WHERE mi.is_available = 1
        ORDER BY mc.name, mi.name
    ''')
    all_menus = cursor.fetchall()
    
    print(f"รายการเมนูทั้งหมด ({len(all_menus)} รายการ):")
    print("=" * 60)
    
    current_category = None
    category_count = 0
    total_count = 0
    
    for category, menu_name, price, item_id, created_at in all_menus:
        if category != current_category:
            if current_category is not None:
                print(f"  รวม: {category_count} รายการ\n")
            print(f"[{category}]")
            current_category = category
            category_count = 0
        
        category_count += 1
        total_count += 1
        print(f"  {category_count:2d}. {menu_name} (฿{price}) [ID: {item_id}]")
        
        # แสดง created_at ถ้ามี
        if created_at:
            print(f"      สร้างเมื่อ: {created_at}")
    
    if current_category is not None:
        print(f"  รวม: {category_count} รายการ\n")
    
    print(f"รวมทั้งหมด: {total_count} รายการ")
    print(f"ต้องลบ: {total_count - 77} รายการ เพื่อให้เหลือ 77 รายการ")
    
    # ตรวจสอบเมนูที่อาจจะซ้ำหรือไม่จำเป็น
    print("\n" + "=" * 60)
    print("ตรวจสอบเมนูที่อาจจะซ้ำ:")
    cursor.execute('''
        SELECT name, COUNT(*) as count
        FROM menu_items
        WHERE is_available = 1
        GROUP BY name
        HAVING COUNT(*) > 1
        ORDER BY count DESC, name
    ''')
    duplicate_menus = cursor.fetchall()
    
    if duplicate_menus:
        print(f"พบเมนูที่ซ้ำ {len(duplicate_menus)} รายการ:")
        for menu_name, count in duplicate_menus:
            print(f"- {menu_name}: {count} รายการ")
            
            # แสดงรายละเอียดของเมนูที่ซ้ำ
            cursor.execute('''
                SELECT mi.item_id, mc.name as category, mi.price, mi.created_at
                FROM menu_items mi
                JOIN menu_categories mc ON mi.category_id = mc.category_id
                WHERE mi.name = ? AND mi.is_available = 1
                ORDER BY mi.item_id
            ''', (menu_name,))
            duplicate_details = cursor.fetchall()
            
            for item_id, category, price, created_at in duplicate_details:
                print(f"    ID: {item_id}, หมวด: {category}, ราคา: ฿{price}, สร้าง: {created_at or 'ไม่ระบุ'}")
    else:
        print("ไม่พบเมนูที่ซ้ำ")
    
    # ตรวจสอบเมนูที่มีราคาผิดปกติ
    print("\n" + "=" * 60)
    print("ตรวจสอบเมนูที่มีราคาผิดปกติ:")
    cursor.execute('''
        SELECT mi.name, mc.name as category, mi.price
        FROM menu_items mi
        JOIN menu_categories mc ON mi.category_id = mc.category_id
        WHERE mi.is_available = 1 AND (mi.price = 0 OR mi.price > 500)
        ORDER BY mi.price DESC
    ''')
    unusual_prices = cursor.fetchall()
    
    if unusual_prices:
        print(f"พบเมนูที่มีราคาผิดปกติ {len(unusual_prices)} รายการ:")
        for menu_name, category, price in unusual_prices:
            print(f"- {menu_name} ({category}): ฿{price}")
    else:
        print("ไม่พบเมนูที่มีราคาผิดปกติ")
    
    conn.close()
    
except Exception as e:
    print(f'เกิดข้อผิดพลาด: {e}')