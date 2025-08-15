import sqlite3
from datetime import datetime

conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

print('=== ยอดขายตามวันที่ ===')

# ตรวจสอบข้อมูลออเดอร์ล่าสุด
cursor.execute('''
    SELECT DATE(created_at, 'localtime') as order_date, 
           SUM(total_amount) as daily_sales, 
           COUNT(*) as orders 
    FROM orders 
    GROUP BY DATE(created_at, 'localtime') 
    ORDER BY order_date DESC 
    LIMIT 10
''')

results = cursor.fetchall()
print('ยอดขายล่าสุด 10 วัน:')
for row in results:
    print(f'{row[0]}: ยอดขาย = {row[1]} บาท, ออเดอร์ = {row[2]} รายการ')

# ตรวจสอบข้อมูลวันนี้โดยเฉพาะ
today = datetime.now().strftime('%Y-%m-%d')
cursor.execute('''
    SELECT COALESCE(SUM(total_amount), 0) as today_sales, 
           COUNT(*) as today_orders 
    FROM orders 
    WHERE DATE(created_at, 'localtime') = ?
''', (today,))

today_result = cursor.fetchone()
print(f'\nวันนี้ ({today}): ยอดขาย = {today_result[0]} บาท, ออเดอร์ = {today_result[1]} รายการ')

conn.close()