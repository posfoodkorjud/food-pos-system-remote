import sqlite3
from datetime import datetime

conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

# ตรวจสอบออเดอร์วันนี้
cursor.execute("""
    SELECT order_id, total_amount, status, created_at 
    FROM orders 
    WHERE DATE(created_at) = DATE('now', 'localtime') 
    ORDER BY created_at
""")

orders = cursor.fetchall()
print('Orders today:')
total = 0
for order in orders:
    print(f'Order {order[0]}: {order[1]} บาท (status: {order[2]}) - {order[3]}')
    if order[2] != 'rejected':
        total += order[1]

print(f'\nTotal non-rejected orders: {total} บาท')
print(f'Number of orders: {len(orders)}')

conn.close()