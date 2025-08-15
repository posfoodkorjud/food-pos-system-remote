import sqlite3
import os

# แสดงเมนูที่อาจจะไม่จำเป็นเพื่อให้เลือกลบ
db_path = 'A_FOOD_POS/FOOD_POS/pos_database.db'
if not os.path.exists(db_path):
    db_path = 'A_FOOD_POS/pos_database.db'
    if not os.path.exists(db_path):
        print("ไม่พบไฟล์ฐานข้อมูล")
        exit(1)

print(f"แสดงเมนูที่อาจจะไม่จำเป็น: {db_path}")
print("=" * 60)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ตรวจสอบจำนวนเมนูปัจจุบัน
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE is_available = 1')
    current_count = cursor.fetchone()[0]
    print(f"จำนวนเมนูปัจจุบัน: {current_count} รายการ")
    print(f"ต้องลบ: {current_count - 77} รายการ เพื่อให้เหลือ 77 รายการ")
    print()
    
    # แสดงเมนูที่มีราคาสูงที่สุด (อาจจะไม่เหมาะสมกับร้านอาหาร)
    print("1. เมนูที่มีราคาสูงที่สุด (อาจจะไม่เหมาะสม):")
    cursor.execute('''
        SELECT mi.item_id, mi.name, mc.name as category, mi.price
        FROM menu_items mi
        JOIN menu_categories mc ON mi.category_id = mc.category_id
        WHERE mi.is_available = 1
        ORDER BY mi.price DESC
        LIMIT 10
    ''')
    expensive_menus = cursor.fetchall()
    
    for item_id, name, category, price in expensive_menus:
        print(f"   ID {item_id}: {name} ({category}) - ฿{price}")
    
    # แสดงเมนูที่สร้างล่าสุด (อาจจะเป็นการทดสอบ)
    print("\n2. เมนูที่สร้างล่าสุด (อาจจะเป็นการทดสอบ):")
    cursor.execute('''
        SELECT mi.item_id, mi.name, mc.name as category, mi.price, mi.created_at
        FROM menu_items mi
        JOIN menu_categories mc ON mi.category_id = mc.category_id
        WHERE mi.is_available = 1 AND mi.created_at IS NOT NULL
        ORDER BY mi.created_at DESC
        LIMIT 10
    ''')
    recent_menus = cursor.fetchall()
    
    for item_id, name, category, price, created_at in recent_menus:
        print(f"   ID {item_id}: {name} ({category}) - ฿{price} [สร้าง: {created_at}]")
    
    # แสดงเมนูที่มีชื่อคล้ายกัน (อาจจะซ้ำความหมาย)
    print("\n3. เมนูที่มีชื่อคล้ายกัน:")
    cursor.execute('''
        SELECT mi.item_id, mi.name, mc.name as category, mi.price
        FROM menu_items mi
        JOIN menu_categories mc ON mi.category_id = mc.category_id
        WHERE mi.is_available = 1
        ORDER BY mi.name
    ''')
    all_menus = cursor.fetchall()
    
    # หาเมนูที่มีคำคล้ายกัน
    similar_groups = {}
    for item_id, name, category, price in all_menus:
        # หาคำหลักในชื่อเมนู
        words = name.replace('ข้าว', '').replace('น้ำ', '').replace('ผัด', '').strip()
        if len(words) > 3:  # เฉพาะคำที่มีความยาวมากกว่า 3 ตัวอักษร
            key = words[:6]  # ใช้ 6 ตัวอักษรแรกเป็น key
            if key not in similar_groups:
                similar_groups[key] = []
            similar_groups[key].append((item_id, name, category, price))
    
    # แสดงกลุ่มที่มีมากกว่า 1 รายการ
    for key, items in similar_groups.items():
        if len(items) > 1:
            print(f"   กลุ่ม '{key}':")
            for item_id, name, category, price in items:
                print(f"     ID {item_id}: {name} ({category}) - ฿{price}")
    
    # แสดงเมนูในหมวดที่มีเมนูมากที่สุด
    print("\n4. หมวดหมู่ที่มีเมนูมากที่สุด:")
    cursor.execute('''
        SELECT mc.name, COUNT(mi.item_id) as count
        FROM menu_categories mc
        LEFT JOIN menu_items mi ON mc.category_id = mi.category_id AND mi.is_available = 1
        WHERE mc.is_active = 1
        GROUP BY mc.name
        ORDER BY count DESC
    ''')
    category_counts = cursor.fetchall()
    
    for cat_name, count in category_counts:
        print(f"   {cat_name}: {count} รายการ")
        if count > 20:  # แสดงเมนูในหมวดที่มีมากกว่า 20 รายการ
            cursor.execute('''
                SELECT mi.item_id, mi.name, mi.price
                FROM menu_items mi
                JOIN menu_categories mc ON mi.category_id = mc.category_id
                WHERE mc.name = ? AND mi.is_available = 1
                ORDER BY mi.price DESC
                LIMIT 5
            ''', (cat_name,))
            expensive_in_cat = cursor.fetchall()
            print(f"     เมนูที่แพงที่สุดใน{cat_name}:")
            for item_id, name, price in expensive_in_cat:
                print(f"       ID {item_id}: {name} - ฿{price}")
    
    print("\n" + "=" * 60)
    print("💡 คำแนะนำ:")
    print("1. ลบเมนูที่มีราคาสูงผิดปกติ (เช่น มากกว่า 200 บาท)")
    print("2. ลบเมนูที่สร้างล่าสุดซึ่งอาจจะเป็นการทดสอบ")
    print("3. ลบเมนูที่มีชื่อคล้ายกันและอาจจะซ้ำความหมาย")
    print("4. ลบเมนูบางรายการในหมวดที่มีเมนูมากเกินไป")
    
    conn.close()
    
except Exception as e:
    print(f'เกิดข้อผิดพลาด: {e}')