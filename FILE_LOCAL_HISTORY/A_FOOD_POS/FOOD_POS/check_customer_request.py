import sqlite3

conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

# Get all distinct customer_request values
cursor.execute('SELECT DISTINCT customer_request FROM order_items WHERE customer_request IS NOT NULL AND customer_request != "" ORDER BY customer_request')
rows = cursor.fetchall()

print('Customer requests in database:')
for row in rows:
    print(f'- "{row[0]}"')

# Get recent orders with customer requests
print('\nRecent orders with customer requests:')
cursor.execute('''
    SELECT oi.order_id, m.name, oi.customer_request 
    FROM order_items oi 
    JOIN menu_items m ON oi.item_id = m.item_id 
    WHERE oi.customer_request IS NOT NULL AND oi.customer_request != "" 
    ORDER BY oi.order_id DESC 
    LIMIT 10
''')
rows = cursor.fetchall()

for row in rows:
    print(f'Order {row[0]}: {row[1]} - Customer Request: "{row[2]}"')
    # แยกส่วนของ customer_request
    if ' | ' in row[2]:
        parts = row[2].split(' | ')
        print(f'  - ส่วนที่ 1 (ตัวเลือกพิเศษ): "{parts[0]}"')
        if len(parts) > 1:
            print(f'  - ส่วนที่ 2 (หมายเหตุ): "{parts[1]}"')
        if len(parts) > 2:
            print(f'  - ส่วนที่ 3: "{parts[2]}"')
    else:
        print(f'  - ข้อมูลเดียว: "{row[2]}"')
    print()

conn.close()