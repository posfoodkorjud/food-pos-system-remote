import sqlite3
import os

# ลบเมนูที่ซ้ำออกจากฐานข้อมูล
db_path = 'A_FOOD_POS/FOOD_POS/pos_database.db'
if not os.path.exists(db_path):
    db_path = 'A_FOOD_POS/pos_database.db'
    if not os.path.exists(db_path):
        print("ไม่พบไฟล์ฐานข้อมูล")
        exit(1)

print(f"ลบเมนูซ้ำจากฐานข้อมูล: {db_path}")
print("=" * 60)

# รายการ ID ที่ต้องลบ (จากผลลัพธ์ก่อนหน้า)
ids_to_remove = [13, 92, 97, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112]

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ตรวจสอบจำนวนเมนูก่อนลบ
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE is_available = 1')
    before_count = cursor.fetchone()[0]
    print(f"จำนวนเมนูก่อนลบ: {before_count} รายการ")
    
    # แสดงรายการที่จะลบ
    print(f"\nรายการที่จะลบ ({len(ids_to_remove)} รายการ):")
    for item_id in ids_to_remove:
        cursor.execute('''
            SELECT mi.name, mc.name as category, mi.price
            FROM menu_items mi
            JOIN menu_categories mc ON mi.category_id = mc.category_id
            WHERE mi.item_id = ?
        ''', (item_id,))
        result = cursor.fetchone()
        if result:
            name, category, price = result
            print(f"- ID {item_id}: {name} ({category}) - ฿{price}")
        else:
            print(f"- ID {item_id}: ไม่พบข้อมูล")
    
    # ยืนยันการลบ
    print(f"\n⚠️  คุณต้องการลบเมนูซ้ำ {len(ids_to_remove)} รายการนี้หรือไม่?")
    print("หลังลบแล้วจะเหลือเมนู 82 รายการ (ต้องลบเพิ่มอีก 5 รายการเพื่อให้เหลือ 77)")
    
    # ลบเมนูที่ซ้ำ
    print("\nกำลังลบเมนูซ้ำ...")
    
    for item_id in ids_to_remove:
        cursor.execute('DELETE FROM menu_items WHERE item_id = ?', (item_id,))
        print(f"✓ ลบ ID {item_id} แล้ว")
    
    # บันทึกการเปลี่ยนแปลง
    conn.commit()
    
    # ตรวจสอบจำนวนเมนูหลังลบ
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE is_available = 1')
    after_count = cursor.fetchone()[0]
    
    print(f"\n" + "=" * 60)
    print("สรุปผลการลบ:")
    print(f"- จำนวนเมนูก่อนลบ: {before_count} รายการ")
    print(f"- จำนวนเมนูที่ลบ: {len(ids_to_remove)} รายการ")
    print(f"- จำนวนเมนูหลังลบ: {after_count} รายการ")
    
    if after_count == 82:
        print("\n✅ ลบเมนูซ้ำสำเร็จ! เหลือ 82 รายการ")
        print("💡 ต้องลบเพิ่มอีก 5 รายการเพื่อให้เหลือ 77 รายการตามที่ต้องการ")
    else:
        print(f"\n⚠️  ผลลัพธ์ไม่ตรงตามคาด (คาดว่าจะเหลือ 82 รายการ)")
    
    # แสดงหมวดหมู่และจำนวนเมนูหลังลบ
    print(f"\nจำนวนเมนูในแต่ละหมวดหลังลบซ้ำ:")
    cursor.execute('''
        SELECT mc.name, COUNT(mi.item_id) as count
        FROM menu_categories mc
        LEFT JOIN menu_items mi ON mc.category_id = mi.category_id AND mi.is_available = 1
        WHERE mc.is_active = 1
        GROUP BY mc.name
        HAVING COUNT(mi.item_id) > 0
        ORDER BY mc.name
    ''')
    categories = cursor.fetchall()
    
    for cat_name, count in categories:
        print(f"- {cat_name}: {count} รายการ")
    
    conn.close()
    print("\n✅ เสร็จสิ้น!")
    
except Exception as e:
    print(f'เกิดข้อผิดพลาด: {e}')
    if 'conn' in locals():
        conn.rollback()
        conn.close()