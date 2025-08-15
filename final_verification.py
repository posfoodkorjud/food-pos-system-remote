import sqlite3
import os

# ยืนยันผลลัพธ์สุดท้าย - ตรวจสอบว่ามีเมนู 77 รายการจริง
db_path = 'A_FOOD_POS/FOOD_POS/pos_database.db'
if not os.path.exists(db_path):
    db_path = 'A_FOOD_POS/pos_database.db'
    if not os.path.exists(db_path):
        print("ไม่พบไฟล์ฐานข้อมูล")
        exit(1)

print(f"ยืนยันผลลัพธ์สุดท้าย: {db_path}")
print("=" * 60)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ตรวจสอบจำนวนเมนูทั้งหมด
    cursor.execute('SELECT COUNT(*) FROM menu_items')
    total_menus = cursor.fetchone()[0]
    
    # ตรวจสอบจำนวนเมนูที่พร้อมจำหน่าย
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE is_available = 1')
    available_menus = cursor.fetchone()[0]
    
    # ตรวจสอบจำนวนเมนูที่ไม่พร้อมจำหน่าย
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE is_available = 0')
    unavailable_menus = cursor.fetchone()[0]
    
    print(f"📊 สรุปข้อมูลเมนูในฐานข้อมูล:")
    print(f"   - เมนูทั้งหมด: {total_menus} รายการ")
    print(f"   - เมนูพร้อมจำหน่าย: {available_menus} รายการ")
    print(f"   - เมนูไม่พร้อมจำหน่าย: {unavailable_menus} รายการ")
    
    # ตรวจสอบจำนวนเมนูในแต่ละหมวดหมู่
    cursor.execute('''
        SELECT mc.name, COUNT(mi.item_id) as count
        FROM menu_categories mc
        LEFT JOIN menu_items mi ON mc.category_id = mi.category_id AND mi.is_available = 1
        WHERE mc.is_active = 1
        GROUP BY mc.name
        ORDER BY count DESC
    ''')
    category_counts = cursor.fetchall()
    
    print(f"\n📋 จำนวนเมนูในแต่ละหมวดหมู่:")
    total_by_category = 0
    for cat_name, count in category_counts:
        if count > 0:
            print(f"   - {cat_name}: {count} รายการ")
            total_by_category += count
    
    print(f"\n🔍 การตรวจสอบ:")
    print(f"   - รวมเมนูจากหมวดหมู่: {total_by_category} รายการ")
    print(f"   - เมนูพร้อมจำหน่ายจากฐานข้อมูล: {available_menus} รายการ")
    
    if available_menus == 77:
        print(f"\n🎉 ✅ สำเร็จ! มีเมนูพร้อมจำหน่าย {available_menus} รายการตามที่ต้องการ")
    else:
        print(f"\n⚠️  ❌ ไม่ตรงตามเป้าหมาย! มีเมนู {available_menus} รายการ (ต้องการ 77 รายการ)")
    
    if total_by_category == available_menus:
        print(f"✅ จำนวนเมนูจากหมวดหมู่ตรงกับฐานข้อมูล")
    else:
        print(f"❌ จำนวนเมนูจากหมวดหมู่ไม่ตรงกับฐานข้อมูล")
    
    # แสดงตัวอย่างเมนูในแต่ละหมวดหมู่
    print(f"\n📝 ตัวอย่างเมนูในแต่ละหมวดหมู่:")
    for cat_name, count in category_counts:
        if count > 0:
            cursor.execute('''
                SELECT mi.item_id, mi.name, mi.price
                FROM menu_items mi
                JOIN menu_categories mc ON mi.category_id = mc.category_id
                WHERE mc.name = ? AND mi.is_available = 1
                ORDER BY mi.price
                LIMIT 3
            ''', (cat_name,))
            sample_menus = cursor.fetchall()
            
            print(f"\n   {cat_name} ({count} รายการ):")
            for item_id, name, price in sample_menus:
                print(f"     - {name} (฿{price})")
            if count > 3:
                print(f"     ... และอีก {count - 3} รายการ")
    
    print(f"\n" + "=" * 60)
    print(f"🏆 การทำความสะอาดฐานข้อมูลเสร็จสิ้น!")
    print(f"📈 ผลลัพธ์: มีเมนูพร้อมจำหน่าย {available_menus} รายการ")
    
    conn.close()
    
except Exception as e:
    print(f'เกิดข้อผิดพลาด: {e}')