import sqlite3

def check_menu_items_structure():
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    # ตรวจสอบโครงสร้างตาราง menu_items
    cursor.execute("PRAGMA table_info(menu_items)")
    columns = cursor.fetchall()
    
    print("โครงสร้างตาราง 'menu_items':")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # ตรวจสอบข้อมูลในตาราง menu_items
    cursor.execute("SELECT * FROM menu_items LIMIT 5")
    rows = cursor.fetchall()
    
    print("\nข้อมูลตัวอย่างในตาราง 'menu_items':")
    for row in rows:
        print(f"  {row}")
    
    conn.close()

if __name__ == "__main__":
    check_menu_items_structure()