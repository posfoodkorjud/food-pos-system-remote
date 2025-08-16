import sqlite3

# เชื่อมต่อฐานข้อมูลในโฟลเดอร์ parent
conn = sqlite3.connect('../pos_database.db')
cursor = conn.cursor()

print("=== ตรวจสอบ Order ID 60 ===")

# ตรวจสอบ order_items สำหรับ order_id 60
cursor.execute('SELECT * FROM order_items WHERE order_id = 60')
items = cursor.fetchall()

print(f"\nOrder items สำหรับ order 60 ({len(items)} รายการ):")
for item in items:
    print(f"  ID: {item[0]}, Order: {item[1]}, Item: {item[2]}, Qty: {item[3]}, Price: {item[4]}, Total: {item[5]}, Special: {item[6]}")

if len(items) == 0:
    print("ไม่พบ order_items สำหรับ order 60!")

# ตรวจสอบ order ใน orders table
cursor.execute('SELECT * FROM orders WHERE order_id = 60')
order = cursor.fetchone()

if order:
    print(f"\nOrder 60 details:")
    print(f"  Order ID: {order[0]}, Table: {order[1]}, Total: {order[2]}, Status: {order[3]}, Created: {order[4]}")
else:
    print("\nไม่พบ order 60 ใน orders table!")

conn.close()
print("\nเสร็จสิ้นการตรวจสอบ")