import sqlite3

# Connect to database
conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

# Check order status
cursor.execute('SELECT order_id, table_id, status, total_amount, created_at, completed_at FROM orders WHERE order_id = 170')
order = cursor.fetchone()

if order:
    print(f'Order 170 details:')
    print(f'Table ID: {order[1]}')
    print(f'Status: {order[2]}')
    print(f'Total: {order[3]} baht')
    print(f'Created: {order[4]}')
    print(f'Completed: {order[5] if order[5] else "Not completed yet"}')
else:
    print('Order 170 not found')

conn.close()