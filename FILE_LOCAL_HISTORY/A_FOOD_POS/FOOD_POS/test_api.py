import sqlite3

conn = sqlite3.connect('pos_database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== ตรวจสอบตาราง menu_items ===")
cursor.execute('SELECT * FROM menu_items LIMIT 5')
menu_items = cursor.fetchall()
print(f"จำนวนเมนู: {len(menu_items)}")
for item in menu_items:
    print(f"ID: {item['item_id']}, Name: {item['name']}")

print("\n=== ตรวจสอบ order_items ===")
cursor.execute('SELECT * FROM order_items LIMIT 5')
order_items = cursor.fetchall()
for item in order_items:
    print(f"Order Item ID: {item['order_item_id']}, Item ID: {item['item_id']}")

print("\n=== ทดสอบ JOIN ===")
cursor.execute('''
    SELECT oi.order_item_id, oi.item_id, mi.item_id as menu_item_id, mi.name
    FROM order_items oi
    LEFT JOIN menu_items mi ON oi.item_id = mi.item_id
    LIMIT 5
''')
joined = cursor.fetchall()
for row in joined:
    print(f"Order Item: {row['order_item_id']}, Item ID: {row['item_id']}, Menu Item ID: {row['menu_item_id']}, Name: {row['name']}")

conn.close()