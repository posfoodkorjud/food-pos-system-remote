import sqlite3
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect('A_FOOD_POS/FOOD_POS/pos_database.db')
cursor = conn.cursor()

print("=== Checking Orders in Database ===")
print(f"Today's date: {datetime.now().strftime('%Y-%m-%d')}")

# Check all orders
cursor.execute("SELECT created_at, total_amount, status FROM orders ORDER BY created_at DESC LIMIT 10")
orders = cursor.fetchall()

print("\nLast 10 orders:")
for order in orders:
    print(f"Date: {order[0]}, Amount: {order[1]}, Status: {order[2]}")

# Check orders for last 7 days
start_date = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')

print(f"\n=== Orders from {start_date} to {end_date} ===")
cursor.execute("""
    SELECT created_at, total_amount, status 
    FROM orders 
    WHERE DATE(created_at) >= ? AND DATE(created_at) <= ? AND status != 'rejected'
    ORDER BY created_at
""", (start_date, end_date))

orders_7days = cursor.fetchall()
total_7days = 0

for order in orders_7days:
    print(f"Date: {order[0]}, Amount: {order[1]}, Status: {order[2]}")
    total_7days += order[1]

print(f"\nTotal for 7 days: {total_7days}")

# Check current week (Monday to Sunday)
today = datetime.now()
days_since_monday = today.weekday()
week_start = (today - timedelta(days=days_since_monday)).strftime('%Y-%m-%d')
week_end = (today - timedelta(days=days_since_monday) + timedelta(days=6)).strftime('%Y-%m-%d')

print(f"\n=== Current Week Orders ({week_start} to {week_end}) ===")
cursor.execute("""
    SELECT created_at, total_amount, status 
    FROM orders 
    WHERE DATE(created_at) >= ? AND DATE(created_at) <= ? AND status != 'rejected'
    ORDER BY created_at
""", (week_start, week_end))

orders_week = cursor.fetchall()
total_week = 0

for order in orders_week:
    print(f"Date: {order[0]}, Amount: {order[1]}, Status: {order[2]}")
    total_week += order[1]

print(f"\nTotal for current week: {total_week}")

conn.close()