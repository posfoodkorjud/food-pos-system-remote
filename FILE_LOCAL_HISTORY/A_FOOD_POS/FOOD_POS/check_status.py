import sqlite3

# เชื่อมต่อฐานข้อมูล
conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

# ตรวจสอบสถานะทั้งหมดใน orders table
print("=== Orders by status ===")
cursor.execute('SELECT status, COUNT(*) FROM orders GROUP BY status')
status_counts = cursor.fetchall()
for status, count in status_counts:
    print(f'{status}: {count}')

# ตรวจสอบ orders ที่มีสถานะ accepted และ pending
print("\n=== Recent accepted/pending orders ===")
cursor.execute('SELECT order_id, table_id, status FROM orders WHERE status IN ("accepted", "pending") ORDER BY order_id DESC LIMIT 10')
rows = cursor.fetchall()
for row in rows:
    print(f'Order {row[0]}, Table {row[1]}: {row[2]}')

# ตรวจสอบสถานะล่าสุดใน order_history_items
print("\n=== Recent order_history_items status ===")
cursor.execute('SELECT order_id, menu_item_id, status FROM order_history_items ORDER BY order_id DESC LIMIT 10')
rows = cursor.fetchall()
for row in rows:
    print(f'Order {row[0]}, Item {row[1]}: {row[2]}')

# ตรวจสอบสถานะทั้งหมดที่มีในระบบ
print("\n=== All unique statuses in order_history_items ===")
cursor.execute('SELECT DISTINCT status, COUNT(*) FROM order_history_items GROUP BY status')
status_counts = cursor.fetchall()
for status, count in status_counts:
    print(f'Status: {status}, Count: {count}')

conn.close()
print("\nDone!")