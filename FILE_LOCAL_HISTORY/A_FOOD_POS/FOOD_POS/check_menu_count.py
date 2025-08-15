import sqlite3

def check_menu_details():
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    # ดูเมนูทั้งหมด
    cursor.execute('''
        SELECT item_id, name, is_available, category_id
        FROM menu_items 
        ORDER BY item_id
    ''')
    items = cursor.fetchall()
    
    print(f"จำนวนเมนูทั้งหมด: {len(items)}")
    print("\n=== เมนูที่ไม่พร้อมให้บริการ (14 รายการ) ===")
    
    unavailable_items = [item for item in items if item[2] == 0]
    for item_id, name, is_available, category_id in unavailable_items:
        print(f"{item_id:3d}. {name} (หมวด: {category_id})")
    
    print(f"\nจำนวนเมนูที่ไม่พร้อมให้บริการ: {len(unavailable_items)}")
    
    # ดูหมวดหมู่
    cursor.execute('SELECT category_id, name FROM menu_categories ORDER BY category_id')
    categories = cursor.fetchall()
    print("\n=== หมวดหมู่ ===")
    for cat_id, cat_name in categories:
        cursor.execute('SELECT COUNT(*) FROM menu_items WHERE category_id = ?', (cat_id,))
        total = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM menu_items WHERE category_id = ? AND is_available = 1', (cat_id,))
        available = cursor.fetchone()[0]
        print(f"{cat_id}. {cat_name}: {available}/{total} รายการ")
    
    conn.close()

if __name__ == "__main__":
    check_menu_details()