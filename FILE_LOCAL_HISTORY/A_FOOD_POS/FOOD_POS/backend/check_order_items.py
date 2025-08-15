import sqlite3

# เชื่อมต่อฐานข้อมูล
conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

# ตรวจสอบ schema ของตาราง order_items
print("=== Schema ของตาราง order_items ===")
cursor.execute('PRAGMA table_info(order_items)')
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# ดึงข้อมูล order_items ล่าสุด 10 รายการ
print("\n=== Order Items ล่าสุด 10 รายการ ===")
cursor.execute('SELECT * FROM order_items ORDER BY order_item_id DESC LIMIT 10')
rows = cursor.fetchall()

if rows:
    for row in rows:
        print(f"ID: {row[0]}, Order: {row[1]}, Item: {row[2]}, Qty: {row[3]}, Price: {row[4]}, Total: {row[5]}, Special: '{row[6]}', Status: {row[7]}")
else:
    print("ไม่พบข้อมูลใน order_items")

# ตรวจสอบ orders ล่าสุด
print("\n=== Orders ล่าสุด 5 รายการ ===")
cursor.execute('SELECT order_id, table_id, status, created_at FROM orders ORDER BY order_id DESC LIMIT 5')
orders = cursor.fetchall()
for order in orders:
    print(f"Order ID: {order[0]}, Table: {order[1]}, Status: {order[2]}, Created: {order[3]}")

conn.close()
print("\nเสร็จสิ้นการตรวจสอบ")