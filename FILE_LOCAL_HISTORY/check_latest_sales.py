import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('A_FOOD_POS/FOOD_POS/pos_database.db')
cursor = conn.cursor()

# Get today's date
today = datetime.now().strftime('%Y-%m-%d')
print(f"Today's date: {today}")

# Check today's orders
print("\n=== Today's Orders ===")
cursor.execute("""
    SELECT order_id, total_amount, created_at, status
    FROM orders 
    WHERE DATE(created_at, 'localtime') = ?
    ORDER BY created_at DESC
""", (today,))

today_orders = cursor.fetchall()
if today_orders:
    total_today = 0
    for order in today_orders:
        print(f"Order ID: {order[0]}, Amount: {order[1]}, Time: {order[2]}, Status: {order[3]}")
        total_today += order[1]
    print(f"\nTotal today's sales: {total_today} baht")
    print(f"Number of orders today: {len(today_orders)}")
else:
    print("No orders found for today")

# Check the last 5 orders regardless of date
print("\n=== Last 5 Orders (Any Date) ===")
cursor.execute("""
    SELECT order_id, total_amount, created_at, status
    FROM orders 
    ORDER BY created_at DESC
    LIMIT 5
""")

last_orders = cursor.fetchall()
for order in last_orders:
    print(f"Order ID: {order[0]}, Amount: {order[1]}, Time: {order[2]}, Status: {order[3]}")

# Check if there are any orders with 89 baht
print("\n=== Orders with 89 baht ===")
cursor.execute("""
    SELECT order_id, total_amount, created_at, status
    FROM orders 
    WHERE total_amount = 89
    ORDER BY created_at DESC
""")

orders_89 = cursor.fetchall()
if orders_89:
    for order in orders_89:
        print(f"Order ID: {order[0]}, Amount: {order[1]}, Time: {order[2]}, Status: {order[3]}")
else:
    print("No orders with 89 baht found")

# Check if there are any orders with 138 baht
print("\n=== Orders with 138 baht ===")
cursor.execute("""
    SELECT order_id, total_amount, created_at, status
    FROM orders 
    WHERE total_amount = 138
    ORDER BY created_at DESC
""")

orders_138 = cursor.fetchall()
if orders_138:
    for order in orders_138:
        print(f"Order ID: {order[0]}, Amount: {order[1]}, Time: {order[2]}, Status: {order[3]}")
else:
    print("No orders with 138 baht found")

conn.close()