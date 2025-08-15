import sqlite3
import os
import shutil
from datetime import datetime

def backup_database():
    """สำรองฐานข้อมูลปัจจุบัน"""
    source_db = 'A_FOOD_POS/pos_database.db'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_db = f'A_FOOD_POS/pos_database_backup_{timestamp}.db'
    
    if os.path.exists(source_db):
        shutil.copy2(source_db, backup_db)
        print(f"✅ สำรองฐานข้อมูลเรียบร้อย: {backup_db}")
        return backup_db
    else:
        print(f"❌ ไม่พบไฟล์ฐานข้อมูล: {source_db}")
        return None

def create_new_database_structure():
    """สร้างโครงสร้างฐานข้อมูลใหม่ตามที่ผู้ใช้ต้องการ"""
    new_db_path = 'A_FOOD_POS/FOOD_POS/backend/pos_database.db'
    
    # สร้างโฟลเดอร์ backend หากไม่มี
    os.makedirs(os.path.dirname(new_db_path), exist_ok=True)
    
    # ลบฐานข้อมูลเก่าหากมี
    if os.path.exists(new_db_path):
        os.remove(new_db_path)
    
    conn = sqlite3.connect(new_db_path)
    cursor = conn.cursor()
    
    print("🔧 สร้างโครงสร้างฐานข้อมูลใหม่...")
    
    # 1. ตาราง tables (ข้อมูลโต๊ะ)
    cursor.execute('''
    CREATE TABLE tables (
        table_id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT NOT NULL,
        status TEXT DEFAULT 'available',
        session_id TEXT,
        checkout_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. ตาราง menu_categories (หมวดหมู่เมนู)
    cursor.execute('''
    CREATE TABLE menu_categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        sort_order INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 3. ตาราง menu_items (รายการเมนู)
    cursor.execute('''
    CREATE TABLE menu_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category_id INTEGER,
        description TEXT,
        food_option_type TEXT,
        image_url TEXT,
        is_available BOOLEAN DEFAULT 1,
        preparation_time INTEGER DEFAULT 15,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES menu_categories(category_id)
    )
    ''')
    
    # 4. ตาราง orders (คำสั่งซื้อปัจจุบัน)
    cursor.execute('''
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_id INTEGER,
        status TEXT DEFAULT 'active',
        total_amount REAL DEFAULT 0,
        bill_status TEXT DEFAULT 'unpaid',
        session_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (table_id) REFERENCES tables(table_id)
    )
    ''')
    
    # 5. ตาราง order_items (รายการอาหารในคำสั่งซื้อ)
    cursor.execute('''
    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        item_id INTEGER,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        total_price REAL NOT NULL,
        customer_request TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
    )
    ''')
    
    # 6. ตาราง order_history (ประวัติคำสั่งซื้อ)
    cursor.execute('''
    CREATE TABLE order_history (
        order_id INTEGER PRIMARY KEY,
        table_id INTEGER,
        total_amount REAL,
        completed_at TIMESTAMP,
        payment_method TEXT,
        session_id TEXT,
        created_at TIMESTAMP,
        FOREIGN KEY (table_id) REFERENCES tables(table_id)
    )
    ''')
    
    # 7. ตาราง order_history_items (รายการอาหารในประวัติ)
    cursor.execute('''
    CREATE TABLE order_history_items (
        history_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        menu_item_id INTEGER,
        quantity INTEGER,
        price REAL,
        customer_request TEXT,
        FOREIGN KEY (order_id) REFERENCES order_history(order_id),
        FOREIGN KEY (menu_item_id) REFERENCES menu_items(item_id)
    )
    ''')
    
    # 8. ตาราง receipts (ใบเสร็จ)
    cursor.execute('''
    CREATE TABLE receipts (
        receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        total_amount REAL,
        payment_method TEXT,
        is_paid BOOLEAN DEFAULT 0,
        promptpay_qr TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        paid_at TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES order_history(order_id)
    )
    ''')
    
    # 9. ตาราง system_config (การตั้งค่าระบบ)
    cursor.execute('''
    CREATE TABLE system_config (
        config_key TEXT PRIMARY KEY,
        config_value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 10. ตาราง option_types (ประเภทตัวเลือก)
    cursor.execute('''
    CREATE TABLE option_types (
        option_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        key TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 11. ตาราง option_values (ค่าตัวเลือก)
    cursor.execute('''
    CREATE TABLE option_values (
        option_value_id INTEGER PRIMARY KEY AUTOINCREMENT,
        option_type INTEGER,
        name TEXT NOT NULL,
        additional_price REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (option_type) REFERENCES option_types(option_type_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ สร้างฐานข้อมูลใหม่เรียบร้อย: {new_db_path}")
    return new_db_path

def insert_initial_data(new_db_path):
    """เพิ่มข้อมูลเริ่มต้น"""
    conn = sqlite3.connect(new_db_path)
    cursor = conn.cursor()
    
    print("📝 เพิ่มข้อมูลเริ่มต้น...")
    
    # เพิ่มโต๊ะ 10 โต๊ะ
    for i in range(1, 11):
        cursor.execute('''
        INSERT INTO tables (table_name, status) 
        VALUES (?, 'available')
        ''', (f'โต๊ะ {i}',))
    
    # เพิ่มหมวดหมู่เมนู 4 หมวด
    categories = [
        ('เมนูข้าว', 'อาหารจานเดียวและข้าวราด', 1),
        ('เครื่องดื่ม', 'เครื่องดื่มทุกประเภท', 2),
        ('ของหวาน', 'ขนมหวานและของหวาน', 3),
        ('อาหารตามสั่ง', 'อาหารตามสั่งทั่วไป', 4)
    ]
    
    for name, desc, sort_order in categories:
        cursor.execute('''
        INSERT INTO menu_categories (name, description, sort_order) 
        VALUES (?, ?, ?)
        ''', (name, desc, sort_order))
    
    # เพิ่มประเภทตัวเลือก
    option_types = [
        ('ระดับความเผ็ด', 'spice_level'),
        ('ระดับความหวาน', 'sweet_level')
    ]
    
    for name, key in option_types:
        cursor.execute('''
        INSERT INTO option_types (name, key) 
        VALUES (?, ?)
        ''', (name, key))
    
    # เพิ่มค่าตัวเลือก
    option_values = [
        (1, 'ไม่เผ็ด', 0),
        (1, 'เผ็ดน้อย', 0),
        (1, 'เผ็ดปานกลาง', 0),
        (1, 'เผ็ดมาก', 0),
        (1, 'เผ็ดมากพิเศษ', 5),
        (2, 'ไม่หวาน', 0),
        (2, 'หวานน้อย', 0),
        (2, 'หวานปานกลาง', 0),
        (2, 'หวานมาก', 0),
        (2, 'หวานพิเศษ', 5)
    ]
    
    for option_type, name, price in option_values:
        cursor.execute('''
        INSERT INTO option_values (option_type, name, additional_price) 
        VALUES (?, ?, ?)
        ''', (option_type, name, price))
    
    # เพิ่มการตั้งค่าระบบ
    cursor.execute('''
    INSERT INTO system_config (config_key, config_value) 
    VALUES ('restaurant_name', 'ร้านอาหาร KORJUD')
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ เพิ่มข้อมูลเริ่มต้นเรียบร้อย")

def migrate_menu_data(old_db_path, new_db_path):
    """ย้ายข้อมูลเมนูจากฐานข้อมูลเก่า"""
    if not os.path.exists(old_db_path):
        print(f"❌ ไม่พบฐานข้อมูลเก่า: {old_db_path}")
        return
    
    print("🔄 ย้ายข้อมูลเมนูจากฐานข้อมูลเก่า...")
    
    # เชื่อมต่อฐานข้อมูลเก่าและใหม่
    old_conn = sqlite3.connect(old_db_path)
    new_conn = sqlite3.connect(new_db_path)
    
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()
    
    try:
        # ย้ายข้อมูลเมนู (เฉพาะ 77 รายการที่ต้องการ)
        old_cursor.execute('''
        SELECT name, price, category_id, description, food_option_type, 
               image_url, is_available, preparation_time
        FROM menu_items 
        WHERE is_available = 1
        LIMIT 77
        ''')
        
        menu_items = old_cursor.fetchall()
        
        for item in menu_items:
            # แมปหมวดหมู่เก่าเป็นใหม่ (ปรับตามความเหมาะสม)
            category_id = min(item[2] if item[2] else 1, 4)
            
            new_cursor.execute('''
            INSERT INTO menu_items (name, price, category_id, description, 
                                  food_option_type, image_url, is_available, preparation_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item[0], item[1], category_id, item[3], item[4], item[5], item[6], item[7]))
        
        print(f"✅ ย้ายข้อมูลเมนู {len(menu_items)} รายการเรียบร้อย")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการย้ายข้อมูล: {e}")
    
    finally:
        new_conn.commit()
        old_conn.close()
        new_conn.close()

def main():
    print("🚀 เริ่มต้นการปรับปรุงฐานข้อมูล...")
    
    # 1. สำรองฐานข้อมูลปัจจุบัน
    backup_path = backup_database()
    
    # 2. สร้างโครงสร้างฐานข้อมูลใหม่
    new_db_path = create_new_database_structure()
    
    # 3. เพิ่มข้อมูลเริ่มต้น
    insert_initial_data(new_db_path)
    
    # 4. ย้ายข้อมูลเมนูจากฐานข้อมูลเก่า
    if backup_path:
        migrate_menu_data('A_FOOD_POS/pos_database.db', new_db_path)
    
    print("\n🎉 การปรับปรุงฐานข้อมูลเสร็จสิ้น!")
    print(f"📁 ฐานข้อมูลใหม่: {new_db_path}")
    print(f"💾 ฐานข้อมูลสำรอง: {backup_path}")

if __name__ == "__main__":
    main()