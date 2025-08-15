import sqlite3
from datetime import datetime

# เชื่อมต่อฐานข้อมูล
conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

print('=== ตรวจสอบออเดอร์ทั้งหมดวันที่ 12/08/2025 ===')
print()

# ตรวจสอบออเดอร์ทั้งหมดในวันที่ 12/08/2025
cursor.execute('''
    SELECT order_id, status, total_amount, created_at, updated_at
    FROM orders 
    WHERE DATE(created_at) = '2025-08-12' 
    ORDER BY created_at
''')

orders = cursor.fetchall()
total_all = 0
total_completed = 0
completed_count = 0

print(f'พบออเดอร์ทั้งหมด: {len(orders)} รายการ')
print()

for order in orders:
    order_id, status, total_amount, created_at, updated_at = order
    amount = total_amount if total_amount else 0
    print(f'Order {order_id}: {status} - {amount} บาท')
    print(f'  สร้าง: {created_at}')
    print(f'  อัปเดต: {updated_at}')
    print()
    
    total_all += amount
    if status == 'completed':
        total_completed += amount
        completed_count += 1

print('=' * 50)
print('สรุปยอดขาย:')
print(f'ยอดรวมทั้งหมด: {total_all} บาท')
print(f'ยอดรวม completed: {total_completed} บาท')
print(f'จำนวนออเดอร์ทั้งหมด: {len(orders)} รายการ')
print(f'จำนวนออเดอร์ completed: {completed_count} รายการ')
print()

# ตรวจสอบข้อมูลจาก API dashboard
print('=== ตรวจสอบข้อมูลจาก API dashboard ===')
try:
    import requests
    response = requests.get('http://localhost:5000/api/dashboard')
    if response.status_code == 200:
        data = response.json()
        print(f'ยอดขายวันนี้จาก API: {data.get("today_sales", "N/A")} บาท')
        print(f'จำนวนออเดอร์วันนี้จาก API: {data.get("today_orders", "N/A")} รายการ')
    else:
        print(f'ไม่สามารถเชื่อมต่อ API ได้ (Status: {response.status_code})')
except Exception as e:
    print(f'เกิดข้อผิดพลาดในการเชื่อมต่อ API: {e}')

conn.close()