import sqlite3

def add_sweet_menu_items():
    """เพิ่มเมนูที่มีตัวเลือกความหวาน"""
    conn = sqlite3.connect('FOOD_POS/pos_database.db')
    cursor = conn.cursor()
    
    # ตรวจสอบหมวดหมู่เครื่องดื่ม
    cursor.execute('SELECT category_id FROM menu_categories WHERE name LIKE "%เครื่องดื่ม%" OR name LIKE "%ของหวาน%" LIMIT 1')
    category = cursor.fetchone()
    
    if not category:
        print("ไม่พบหมวดหมู่เครื่องดื่มหรือของหวาน")
        return
    
    category_id = category[0]
    print(f"ใช้หมวดหมู่ ID: {category_id}")
    
    # เมนูที่มีตัวเลือกความหวาน
    sweet_items = [
        ("ชาไทยเย็น", 35, category_id, "ชาไทยเย็นหวานมัน", "sweet"),
        ("ชาเขียวเย็น", 35, category_id, "ชาเขียวเย็นหวานมัน", "sweet"),
        ("กาแฟเย็น", 40, category_id, "กาแฟเย็นหอมกรุ่น", "sweet"),
        ("โกโก้เย็น", 40, category_id, "โกโก้เย็นหวานหอม", "sweet"),
        ("นมชมพู", 35, category_id, "นมชมพูหวานเย็น", "sweet"),
        ("ลาเต้เย็น", 45, category_id, "ลาเต้เย็นหอมนุ่มลิ้น", "sweet")
    ]
    
    for name, price, cat_id, description, option_type in sweet_items:
        try:
            cursor.execute('''
                INSERT INTO menu_items (name, price, category_id, description, food_option_type, is_available)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (name, price, cat_id, description, option_type))
            print(f"เพิ่มเมนู: {name} (ตัวเลือกความหวาน)")
        except sqlite3.IntegrityError:
            # อัปเดตเมนูที่มีอยู่แล้ว
            cursor.execute('''
                UPDATE menu_items 
                SET food_option_type = ?, is_available = 1
                WHERE name = ?
            ''', (option_type, name))
            print(f"อัปเดตเมนู: {name} (เพิ่มตัวเลือกความหวาน)")
    
    conn.commit()
    conn.close()
    print("เพิ่มเมนูที่มีตัวเลือกความหวานเรียบร้อยแล้ว!")

if __name__ == "__main__":
    add_sweet_menu_items()