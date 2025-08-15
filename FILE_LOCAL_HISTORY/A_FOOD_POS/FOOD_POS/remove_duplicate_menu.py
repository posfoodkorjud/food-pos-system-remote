import sqlite3

def remove_duplicate_menu_items():
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    # ดูเมนูที่ไม่พร้อมให้บริการ ID 79-91
    cursor.execute('''
        SELECT item_id, name, category_id
        FROM menu_items 
        WHERE item_id >= 79 AND item_id <= 91 AND is_available = 0
        ORDER BY item_id
    ''')
    duplicate_items = cursor.fetchall()
    
    print("เมนูที่จะลบ (ID 79-91):")
    for item_id, name, category_id in duplicate_items:
        print(f"{item_id:3d}. {name} (หมวด: {category_id})")
    
    # ลบเมนูเหล่านี้
    cursor.execute('DELETE FROM menu_items WHERE item_id >= 79 AND item_id <= 91')
    deleted_count = cursor.rowcount
    
    print(f"\nลบเมนูแล้ว {deleted_count} รายการ")
    
    # ตรวจสอบจำนวนเมนูหลังลบ
    cursor.execute('SELECT COUNT(*) FROM menu_items')
    total_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE is_available = 1')
    available_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE is_available = 0')
    unavailable_count = cursor.fetchone()[0]
    
    print(f"\nจำนวนเมนูหลังลบ:")
    print(f"ทั้งหมด: {total_count}")
    print(f"พร้อมให้บริการ: {available_count}")
    print(f"ไม่พร้อมให้บริการ: {unavailable_count}")
    
    conn.commit()
    conn.close()
    
    print("\nเสร็จสิ้น!")

if __name__ == "__main__":
    remove_duplicate_menu_items()