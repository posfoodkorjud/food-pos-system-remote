import sqlite3

# เชื่อมต่อฐานข้อมูล
conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

# ตรวจสอบตารางในฐานข้อมูล
print("Tables in database:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

print("\n" + "="*50)

# ตรวจสอบข้อมูลออเดอร์ 179
print("Checking order 179...")
try:
    cursor.execute("SELECT * FROM orders WHERE id = 179")
    order = cursor.fetchone()
    if order:
        print(f"Order found: {order}")
    else:
        print("Order 179 not found")
except Exception as e:
    print(f"Error checking orders table: {e}")

# ตรวจสอบรายการในออเดอร์ 179
print("\nChecking order items...")
try:
    # ลองหาตารางที่เก็บรายการออเดอร์
    possible_tables = ['order_items', 'orderitems', 'items', 'order_details']
    for table_name in possible_tables:
        try:
            cursor.execute(f"SELECT * FROM {table_name} WHERE order_id = 179")
            items = cursor.fetchall()
            if items:
                print(f"Found items in table '{table_name}':")
                for item in items:
                    print(f"  {item}")
                break
        except:
            continue
    else:
        print("No order items table found or no items for order 179")
except Exception as e:
    print(f"Error: {e}")

conn.close()