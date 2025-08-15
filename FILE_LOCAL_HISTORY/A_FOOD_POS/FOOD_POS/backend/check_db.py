import sqlite3

# ตรวจสอบ pos_database.db
print("=== Checking pos_database.db ===")
conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

# ตรวจสอบตารางทั้งหมด
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in pos_database.db:")
for table in tables:
    print(f"  - {table[0]}")

# ตรวจสอบ schema ของตาราง order_items
if any('order_items' in table for table in tables):
    print("\nSchema of order_items table:")
    cursor.execute("PRAGMA table_info(order_items)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
else:
    print("\nTable 'order_items' not found in pos_database.db!")

# ตรวจสอบข้อมูลหมวดหมู่
print("\nMenu Categories:")
cursor.execute("SELECT * FROM menu_categories;")
cats = cursor.fetchall()
for cat in cats:
    print(f"  ID: {cat[0]}, Name: {cat[1]}")

conn.close()

# ตรวจสอบ food_pos.db
print("\n=== Checking food_pos.db ===")
conn = sqlite3.connect('food_pos.db')
cursor = conn.cursor()

# ตรวจสอบตารางทั้งหมด
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in food_pos.db:")
for table in tables:
    print(f"  - {table[0]}")

conn.close()