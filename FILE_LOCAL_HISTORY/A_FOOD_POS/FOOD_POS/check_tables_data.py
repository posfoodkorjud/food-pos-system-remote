import sqlite3

def check_tables_data():
    try:
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ตรวจสอบโครงสร้างตาราง tables
        cursor.execute("PRAGMA table_info(tables)")
        columns = cursor.fetchall()
        print("Tables structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        print("\n" + "="*50 + "\n")
        
        # ตรวจสอบข้อมูลในตาราง tables
        cursor.execute('SELECT table_id, table_name, created_at, checkout_at FROM tables LIMIT 10')
        rows = cursor.fetchall()
        print("Tables data:")
        for row in rows:
            print(f"Table ID: {row[0]}, Name: {row[1]}, Created: {row[2]}, Checkout: {row[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_tables_data()