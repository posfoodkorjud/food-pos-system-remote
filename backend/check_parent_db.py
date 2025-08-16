import sqlite3

# เชื่อมต่อฐานข้อมูลในโฟลเดอร์ parent
conn = sqlite3.connect('../pos_database.db')
cursor = conn.cursor()

print("=== ตรวจสอบฐานข้อมูลในโฟลเดอร์ parent ===")

# ตรวจสอบ order_items ล่าสุด
print("\n=== Order Items ล่าสุด 5 รายการ ===")
cursor.execute('SELECT * FROM order_items ORDER BY order_item_id DESC LIMIT 5')
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

if orders:
    for order in orders:
        print(f"Order ID: {order[0]}, Table: {order[1]}, Status: {order[2]}, Created: {order[3]}")
else:
    print("ไม่พบข้อมูลใน orders")

# ตรวจสอบจำนวนรายการทั้งหมด
print("\n=== สถิติข้อมูล ===")
cursor.execute('SELECT COUNT(*) FROM orders')
order_count = cursor.fetchone()[0]
print(f"จำนวน orders ทั้งหมด: {order_count}")

cursor.execute('SELECT COUNT(*) FROM order_items')
item_count = cursor.fetchone()[0]
print(f"จำนวน order_items ทั้งหมด: {item_count}")

conn.close()
print("\nเสร็จสิ้นการตรวจสอบ")