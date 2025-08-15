import sqlite3

def check_table_structure():
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    # ตรวจสอบโครงสร้างตาราง tables
    cursor.execute("PRAGMA table_info(tables)")
    columns = cursor.fetchall()
    
    print("โครงสร้างตาราง 'tables':")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # ตรวจสอบข้อมูลในตาราง tables
    cursor.execute("SELECT * FROM tables LIMIT 5")
    rows = cursor.fetchall()
    
    print("\nข้อมูลตัวอย่างในตาราง 'tables':")
    for row in rows:
        print(f"  {row}")
    
    conn.close()

if __name__ == "__main__":
    check_table_structure()