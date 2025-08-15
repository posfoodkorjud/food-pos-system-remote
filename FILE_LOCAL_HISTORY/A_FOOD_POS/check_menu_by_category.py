import sqlite3

conn = sqlite3.connect('FOOD_POS/pos_database.db')
cursor = conn.cursor()

# ตรวจสอบเมนูในแต่ละหมวดหมู่
category_ids = [736, 737, 738, 739, 740]

for category_id in category_ids:
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE category_id = ? AND is_available = 1', (category_id,))
    count = cursor.fetchone()[0]
    
    cursor.execute('SELECT name FROM menu_categories WHERE category_id = ?', (category_id,))
    category_name = cursor.fetchone()[0]
    
    print(f"Category {category_id} ({category_name}): {count} available items")
    
    # แสดงตัวอย่างเมนู 3 รายการแรกในแต่ละหมวดหมู่
    cursor.execute('SELECT item_id, name, price FROM menu_items WHERE category_id = ? AND is_available = 1 LIMIT 3', (category_id,))
    items = cursor.fetchall()
    for item in items:
        print(f"  - {item[0]}: {item[1]} (฿{item[2]})")
    print()

conn.close()