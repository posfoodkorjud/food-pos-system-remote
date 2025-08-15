import sqlite3
import os

# ลบเมนู 5 รายการสุดท้ายเพื่อให้เหลือ 77 รายการ
db_path = 'A_FOOD_POS/FOOD_POS/pos_database.db'
if not os.path.exists(db_path):
    db_path = 'A_FOOD_POS/pos_database.db'
    if not os.path.exists(db_path):
        print("ไม่พบไฟล์ฐานข้อมูล")
        exit(1)

print(f"ลบเมนู 5 รายการสุดท้าย: {db_path}")
print("=" * 50)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ตรวจสอบจำนวนเมนูปัจจุบัน
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE is_available = 1')
    current_count = cursor.fetchone()[0]
    print(f"จำนวนเมนูปัจจุบัน: {current_count} รายการ")
    
    if current_count <= 77:
        print("✅ จำนวนเมนูอยู่ในเป้าหมายแล้ว!")
        conn.close()
        exit(0)
    
    # หาเมนูที่ควรลบ (เรียงตามเกณฑ์ต่างๆ)
    menus_to_remove = []
    
    # 1. เมนูที่มีราคาสูงผิดปกติ (มากกว่า 200 บาท)
    cursor.execute('''
        SELECT mi.item_id, mi.name, mc.name as category, mi.price
        FROM menu_items mi
        JOIN menu_categories mc ON mi.category_id = mc.category_id
        WHERE mi.is_available = 1 AND mi.price > 200
        ORDER BY mi.price DESC
    ''')
    expensive_menus = cursor.fetchall()
    
    print("\n1. เมนูที่มีราคาสูงผิดปกติ (> 200 บาท):")
    for item_id, name, category, price in expensive_menus:
        print(f"   ID {item_id}: {name} ({category}) - ฿{price}")
        menus_to_remove.append(item_id)
    
    # 2. เมนูที่มีราคาสูงในหมวดเมนูข้าว (มากกว่า 80 บาท)
    if len(menus_to_remove) < 5:
        cursor.execute('''
            SELECT mi.item_id, mi.name, mc.name as category, mi.price
            FROM menu_items mi
            JOIN menu_categories mc ON mi.category_id = mc.category_id
            WHERE mi.is_available = 1 AND mc.name = 'เมนูข้าว' AND mi.price > 80
            AND mi.item_id NOT IN ({}) 
            ORDER BY mi.price DESC
        '''.format(','.join(map(str, menus_to_remove)) if menus_to_remove else '0'))
        expensive_rice = cursor.fetchall()
        
        print("\n2. เมนูข้าวที่มีราคาสูง (> 80 บาท):")
        for item_id, name, category, price in expensive_rice:
            if len(menus_to_remove) < 5:
                print(f"   ID {item_id}: {name} ({category}) - ฿{price}")
                menus_to_remove.append(item_id)
    
    # 3. เมนูที่สร้างล่าสุด (อาจจะเป็นการทดสอบ)
    if len(menus_to_remove) < 5:
        cursor.execute('''
            SELECT mi.item_id, mi.name, mc.name as category, mi.price, mi.created_at
            FROM menu_items mi
            JOIN menu_categories mc ON mi.category_id = mc.category_id
            WHERE mi.is_available = 1 AND mi.created_at IS NOT NULL
            AND mi.item_id NOT IN ({})
            ORDER BY mi.created_at DESC
        '''.format(','.join(map(str, menus_to_remove)) if menus_to_remove else '0'))
        recent_menus = cursor.fetchall()
        
        print("\n3. เมนูที่สร้างล่าสุด:")
        for item_id, name, category, price, created_at in recent_menus:
            if len(menus_to_remove) < 5:
                print(f"   ID {item_id}: {name} ({category}) - ฿{price} [สร้าง: {created_at}]")
                menus_to_remove.append(item_id)
    
    # 4. เมนูที่มี ID สูงสุด (เมนูที่เพิ่มล่าสุด)
    if len(menus_to_remove) < 5:
        cursor.execute('''
            SELECT mi.item_id, mi.name, mc.name as category, mi.price
            FROM menu_items mi
            JOIN menu_categories mc ON mi.category_id = mc.category_id
            WHERE mi.is_available = 1
            AND mi.item_id NOT IN ({})
            ORDER BY mi.item_id DESC
        '''.format(','.join(map(str, menus_to_remove)) if menus_to_remove else '0'))
        latest_ids = cursor.fetchall()
        
        print("\n4. เมนูที่มี ID สูงสุด:")
        for item_id, name, category, price in latest_ids:
            if len(menus_to_remove) < 5:
                print(f"   ID {item_id}: {name} ({category}) - ฿{price}")
                menus_to_remove.append(item_id)
    
    # จำกัดให้ลบแค่ 5 รายการ
    menus_to_remove = menus_to_remove[:5]
    
    print(f"\n=" * 50)
    print(f"จะลบเมนู {len(menus_to_remove)} รายการ: {menus_to_remove}")
    
    # ยืนยันการลบ
    confirm = input("\nยืนยันการลบ? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ ยกเลิกการลบ")
        conn.close()
        exit(0)
    
    # ลบเมนู
    for item_id in menus_to_remove:
        cursor.execute('DELETE FROM menu_items WHERE item_id = ?', (item_id,))
        print(f"✓ ลบ ID {item_id} แล้ว")
    
    conn.commit()
    
    # ตรวจสอบจำนวนเมนูหลังลบ
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE is_available = 1')
    final_count = cursor.fetchone()[0]
    
    # แสดงจำนวนเมนูในแต่ละหมวดหลังลบ
    cursor.execute('''
        SELECT mc.name, COUNT(mi.item_id) as count
        FROM menu_categories mc
        LEFT JOIN menu_items mi ON mc.category_id = mi.category_id AND mi.is_available = 1
        WHERE mc.is_active = 1
        GROUP BY mc.name
        ORDER BY count DESC
    ''')
    category_counts = cursor.fetchall()
    
    print("\n" + "=" * 50)
    print("สรุปผลการลบ:")
    print(f"- จำนวนเมนูก่อนลบ: {current_count} รายการ")
    print(f"- จำนวนเมนูที่ลบ: {len(menus_to_remove)} รายการ")
    print(f"- จำนวนเมนูหลังลบ: {final_count} รายการ")
    
    if final_count == 77:
        print("\n🎉 สำเร็จ! ตอนนี้มีเมนู 77 รายการตามที่ต้องการ")
    else:
        print(f"\n⚠️  ยังเหลือ {final_count} รายการ (ต้องการ 77 รายการ)")
    
    print("\nจำนวนเมนูในแต่ละหมวดหลังลบ:")
    for cat_name, count in category_counts:
        print(f"- {cat_name}: {count} รายการ")
    
    print("\n✅ เสร็จสิ้น!")
    
    conn.close()
    
except Exception as e:
    print(f'เกิดข้อผิดพลาด: {e}')