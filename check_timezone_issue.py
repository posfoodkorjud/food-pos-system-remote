import sqlite3
import datetime
from datetime import timezone
import time
import os

print("=== ตรวจสอบปัญหาเวลาและวันที่ ===")

# ตรวจสอบเวลาของระบบ
print("\n1. เวลาของระบบ:")
print(f"   datetime.now(): {datetime.datetime.now()}")
print(f"   datetime.now().strftime('%Y-%m-%d'): {datetime.datetime.now().strftime('%Y-%m-%d')}")
print(f"   datetime.utcnow(): {datetime.datetime.utcnow()}")
print(f"   time.time(): {time.time()}")
print(f"   time.localtime(): {time.localtime()}")

# ตรวจสอบ timezone
print(f"\n2. Timezone:")
print(f"   TZ environment: {os.environ.get('TZ', 'Not set')}")
try:
    import pytz
    local_tz = pytz.timezone('Asia/Bangkok')
    bangkok_time = datetime.datetime.now(local_tz)
    print(f"   Bangkok time: {bangkok_time}")
except:
    print("   pytz not available")

# ตรวจสอบฐานข้อมูล
print("\n3. ตรวจสอบฐานข้อมูล:")
conn = sqlite3.connect('A_FOOD_POS/FOOD_POS/pos_database.db')
cursor = conn.cursor()

# ตรวจสอบ SQLite datetime functions
print("\n   SQLite datetime functions:")
cursor.execute("SELECT datetime('now')")
print(f"   datetime('now'): {cursor.fetchone()[0]}")

cursor.execute("SELECT date('now')")
print(f"   date('now'): {cursor.fetchone()[0]}")

cursor.execute("SELECT datetime('now', 'localtime')")
print(f"   datetime('now', 'localtime'): {cursor.fetchone()[0]}")

cursor.execute("SELECT date('now', 'localtime')")
print(f"   date('now', 'localtime'): {cursor.fetchone()[0]}")

# ตรวจสอบออเดอร์ล่าสุด
print("\n4. ออเดอร์ล่าสุด 5 รายการ:")
cursor.execute("""
    SELECT order_id, total_amount, created_at, 
           datetime(created_at, 'localtime') as local_time,
           date(created_at, 'localtime') as local_date
    FROM orders 
    ORDER BY created_at DESC 
    LIMIT 5
""")

orders = cursor.fetchall()
for order in orders:
    print(f"   Order {order[0]}: {order[1]} บาท")
    print(f"     created_at: {order[2]}")
    print(f"     local_time: {order[3]}")
    print(f"     local_date: {order[4]}")
    print()

# ตรวจสอบออเดอร์ที่มีจำนวน 49 และ 89
print("\n5. ออเดอร์ 49 และ 89 บาท:")
for amount in [49, 89]:
    cursor.execute("""
        SELECT order_id, total_amount, created_at, 
               datetime(created_at, 'localtime') as local_time,
               date(created_at, 'localtime') as local_date
        FROM orders 
        WHERE total_amount = ?
        ORDER BY created_at DESC
    """, (amount,))
    
    orders = cursor.fetchall()
    print(f"\n   ออเดอร์ {amount} บาท:")
    for order in orders:
        print(f"     Order {order[0]}: {order[1]} บาท")
        print(f"       created_at (UTC): {order[2]}")
        print(f"       local_time: {order[3]}")
        print(f"       local_date: {order[4]}")

conn.close()

print("\n=== สรุป ===")
print("หากเวลาในฐานข้อมูลเป็น UTC และเวลาท้องถิ่นต่างกัน")
print("อาจทำให้เกิดความสับสนเรื่องวันที่")