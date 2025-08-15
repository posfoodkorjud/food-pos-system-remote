import sqlite3
from datetime import datetime

# เชื่อมต่อฐานข้อมูล
conn = sqlite3.connect('pos_database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# ใช้เวลาท้องถิ่น
now = datetime.now()
today_date = now.strftime('%Y-%m-%d')

print(f"วันที่ปัจจุบัน: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"ตรวจสอบยอดขายวันที่: {today_date}")
print()

# ตรวจสอบโครงสร้างตาราง orders
print("โครงสร้างตาราง orders:")
cursor.execute("PRAGMA table_info(orders)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col['name']} - {col['type']}")
print()

# ตรวจสอบออเดอร์ทั้งหมดในวันนี้
query = """
    SELECT order_id, table_number, status, total, created_at, updated_at
    FROM orders 
    WHERE DATE(created_at) = DATE('now', 'localtime')
    ORDER BY created_at DESC
"""

try:
    cursor.execute(query)
    today_orders = cursor.fetchall()
    
    print(f"ออเดอร์ทั้งหมดในวันนี้: {len(today_orders)} รายการ")
    print()
    
    if today_orders:
        total_today = 0
        completed_today = 0
        
        for order in today_orders:
            print(f"Order ID: {order['order_id']}, โต๊ะ: {order['table_number']}, สถานะ: {order['status']}, ยอดรวม: {order['total']}, เวลา: {order['created_at']}")
            
            if order['status'] == 'completed':
                completed_today += 1
                total_today += order['total']
        
        print()
        print(f"ออเดอร์ที่เสร็จสิ้นในวันนี้: {completed_today} รายการ")
        print(f"ยอดขายรวมวันนี้: {total_today} บาท")
    else:
        print("ไม่มีออเดอร์ในวันนี้")
        
except Exception as e:
    print(f"เกิดข้อผิดพลาด: {e}")
    
    # ลองใช้ query อื่น
    print("\nลองดูข้อมูลออเดอร์ล่าสุด 5 รายการ:")
    try:
        cursor.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 5")
        recent_orders = cursor.fetchall()
        
        for order in recent_orders:
            print(f"Order: {dict(order)}")
    except Exception as e2:
        print(f"ไม่สามารถดึงข้อมูลได้: {e2}")

conn.close()