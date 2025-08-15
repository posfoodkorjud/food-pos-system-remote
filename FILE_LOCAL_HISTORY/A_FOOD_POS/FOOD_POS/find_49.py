import sqlite3
from datetime import datetime

conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

print('=== ค้นหาออเดอร์ที่มียอด 49 บาท ===')

cursor.execute('''
    SELECT order_id, table_id, total_amount, DATE(created_at, 'localtime'), created_at 
    FROM orders 
    WHERE total_amount = 49 
    ORDER BY created_at DESC
''')

results = cursor.fetchall()
print(f'พบออเดอร์ที่มียอด 49 บาท จำนวน {len(results)} รายการ:')
for row in results:
    print(f'Order ID: {row[0]}, Table: {row[1]}, Amount: {row[2]}, Date: {row[3]}, Time: {row[4]}')

# ตรวจสอบออเดอร์ล่าสุด 10 รายการ
print('\n=== ออเดอร์ล่าสุด 10 รายการ ===')
cursor.execute('''
    SELECT order_id, table_id, total_amount, DATE(created_at, 'localtime'), created_at 
    FROM orders 
    ORDER BY created_at DESC 
    LIMIT 10
''')

recent_orders = cursor.fetchall()
for row in recent_orders:
    print(f'Order ID: {row[0]}, Table: {row[1]}, Amount: {row[2]}, Date: {row[3]}, Time: {row[4]}')

# ตรวจสอบวันนี้
today = datetime.now().strftime('%Y-%m-%d')
print(f'\n=== ออเดอร์วันนี้ ({today}) ===')
cursor.execute('''
    SELECT order_id, table_id, total_amount, created_at 
    FROM orders 
    WHERE DATE(created_at, 'localtime') = ? 
    ORDER BY created_at DESC
''', (today,))

today_orders = cursor.fetchall()
print(f'พบออเดอร์วันนี้ จำนวน {len(today_orders)} รายการ:')
for row in today_orders:
    print(f'Order ID: {row[0]}, Table: {row[1]}, Amount: {row[2]}, Time: {row[3]}')

conn.close()