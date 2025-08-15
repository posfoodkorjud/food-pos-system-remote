import sqlite3
import os

# นับเมนูที่ซ้ำและคำนวณจำนวนที่ต้องลบ
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
    
    # หาเมนูที่ซ้ำ
    cursor.execute('''
        SELECT name, COUNT(*) as count
        FROM menu_items
        WHERE is_available = 1
        GROUP BY name
        HAVING COUNT(*) > 1
        ORDER BY count DESC, name
    ''')
    duplicate_menus = cursor.fetchall()
    
    total_duplicates = 0
    items_to_remove = 0
    
    print(f"เมนูที่ซ้ำ ({len(duplicate_menus)} รายการ):")
    print("-" * 60)
    
    for menu_name, count in duplicate_menus:
        total_duplicates += count
        items_to_remove += (count - 1)  # เก็บไว้ 1 รายการ ลบที่เหลือ
        print(f"- {menu_name}: {count} รายการ (ลบ {count-1} รายการ)")
        
        # แสดงรายละเอียดของเมนูที่ซ้ำ
        cursor.execute('''
            SELECT mi.item_id, mc.name as category, mi.price, mi.created_at
            FROM menu_items mi
            JOIN menu_categories mc ON mi.category_id = mc.category_id
            WHERE mi.name = ? AND mi.is_available = 1
            ORDER BY mi.created_at, mi.item_id
        ''', (menu_name,))
        duplicate_details = cursor.fetchall()
        
        for i, (item_id, category, price, created_at) in enumerate(duplicate_details):
            status = "[เก็บไว้]" if i == 0 else "[ลบ]"
            print(f"    {status} ID: {item_id}, หมวด: {category}, ราคา: ฿{price}, สร้าง: {created_at or 'ไม่ระบุ'}")
        print()
    
    # สรุปผล
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE is_available = 1')
    current_total = cursor.fetchone()[0]
    
    print("=" * 60)
    print("สรุป:")
    print(f"- เมนูทั้งหมดปัจจุบัน: {current_total} รายการ")
    print(f"- เมนูที่ซ้ำทั้งหมด: {total_duplicates} รายการ")
    print(f"- รายการที่ต้องลบ: {items_to_remove} รายการ")
    print(f"- เมนูที่เหลือหลังลบซ้ำ: {current_total - items_to_remove} รายการ")
    
    target = 77
    remaining_after_dedup = current_total - items_to_remove
    
    if remaining_after_dedup == target:
        print(f"\n✅ หลังลบเมนูซ้ำแล้ว จะเหลือ {target} รายการพอดี!")
    elif remaining_after_dedup > target:
        additional_to_remove = remaining_after_dedup - target
        print(f"\n⚠️  หลังลบเมนูซ้ำแล้ว ยังเหลือ {remaining_after_dedup} รายการ")
        print(f"   ต้องลบเพิ่มอีก {additional_to_remove} รายการ เพื่อให้เหลือ {target} รายการ")
    else:
        print(f"\n❌ หลังลบเมนูซ้ำแล้ว จะเหลือเพียง {remaining_after_dedup} รายการ (น้อยกว่า {target})")
    
    # แสดงรายการ ID ที่ควรลบ
    if items_to_remove > 0:
        print("\n" + "=" * 60)
        print("รายการ ID ที่ควรลบ:")
        ids_to_remove = []
        
        for menu_name, count in duplicate_menus:
            cursor.execute('''
                SELECT item_id
                FROM menu_items
                WHERE name = ? AND is_available = 1
                ORDER BY created_at, item_id
                LIMIT -1 OFFSET 1
            ''', (menu_name,))
            duplicate_ids = cursor.fetchall()
            for (item_id,) in duplicate_ids:
                ids_to_remove.append(item_id)
        
        print(f"IDs ที่ต้องลบ: {', '.join(map(str, sorted(ids_to_remove)))}")
        print(f"จำนวน: {len(ids_to_remove)} รายการ")
    
    conn.close()
    
except Exception as e:
    print(f'เกิดข้อผิดพลาด: {e}')