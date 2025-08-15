import sqlite3
from datetime import datetime

# เชื่อมต่อฐานข้อมูล
conn = sqlite3.connect('pos_database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("ตรวจสอบออเดอร์ล่าสุด 10 รายการ:")
print("=" * 50)

# ดูออเดอร์ล่าสุด 10 รายการ
cursor.execute("SELECT * FROM orders ORDER BY order_id DESC LIMIT 10")
latest_orders = cursor.fetchall()

for i, order in enumerate(latest_orders, 1):
    print(f"{i}. Order ID: {order['order_id']}")
    print(f"   โต๊ะ: {order['table_id']}")
    print(f"   สถานะ: {order['status']}")
    print(f"   ยอดรวม: {order['total_amount']}")
    print(f"   สร้างเมื่อ: {order['created_at']}")
    print(f"   อัพเดทเมื่อ: {order['updated_at']}")
    print(f"   เสร็จสิ้นเมื่อ: {order['completed_at']}")
    print("-" * 30)

print("\nตรวจสอบออเดอร์ที่มี order_id = 162:")
cursor.execute("SELECT * FROM orders WHERE order_id = 162")
order_162 = cursor.fetchone()

if order_162:
    print(f"พบออเดอร์ ID 162:")
    print(f"โต๊ะ: {order_162['table_id']}")
    print(f"สถานะ: {order_162['status']}")
    print(f"ยอดรวม: {order_162['total_amount']}")
    print(f"สร้างเมื่อ: {order_162['created_at']}")
else:
    print("ไม่พบออเดอร์ ID 162")

print("\nตรวจสอบออเดอร์ในวันนี้ (2025-08-10):")
cursor.execute("SELECT * FROM orders WHERE DATE(created_at) = '2025-08-10' ORDER BY created_at DESC")
today_orders = cursor.fetchall()

if today_orders:
    print(f"พบออเดอร์ในวันนี้ {len(today_orders)} รายการ:")
    for order in today_orders:
        print(f"Order ID: {order['order_id']}, สถานะ: {order['status']}, ยอดรวม: {order['total_amount']}, เวลา: {order['created_at']}")
else:
    print("ไม่พบออเดอร์ในวันนี้")

conn.close()