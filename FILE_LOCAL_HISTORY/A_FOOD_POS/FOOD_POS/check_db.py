import sqlite3

conn = sqlite3.connect('pos_database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== ตรวจสอบข้อมูลในฐานข้อมูล ===")

# ตรวจสอบออเดอร์
cursor.execute('SELECT * FROM orders')
orders = cursor.fetchall()
print(f"\nจำนวนออเดอร์ทั้งหมด: {len(orders)}")
for order in orders:
    print(f"Order ID: {order['order_id']}, Table: {order['table_id']}, Status: {order['status']}")

# ตรวจสอบรายการออเดอร์
cursor.execute('SELECT * FROM order_items')
order_items = cursor.fetchall()
print(f"\nจำนวนรายการออเดอร์ทั้งหมด: {len(order_items)}")
for item in order_items:
    print(f"Order Item ID: {item['order_item_id']}, Order ID: {item['order_id']}, Status: {item['status']}")

# ตรวจสอบโต๊ะ
cursor.execute('SELECT * FROM tables')
tables = cursor.fetchall()
print(f"\nจำนวนโต๊ะทั้งหมด: {len(tables)}")
for table in tables:
    print(f"Table ID: {table['table_id']}, Name: {table['table_name']}, Status: {table['status']}")

conn.close()
print("\n=== เสร็จสิ้นการตรวจสอบ ===")