import sqlite3
from datetime import datetime, timedelta

def check_orders_table():
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    # ตรวจสอบข้อมูลล่าสุด
    print("Latest orders data:")
    cursor.execute('SELECT order_id, session_id, total_amount, created_at FROM orders ORDER BY created_at DESC LIMIT 10')
    for row in cursor.fetchall():
        print(row)
    
    # ตรวจสอบยอดรวมทั้งหมด
    print("\nTotal summary:")
    cursor.execute('SELECT COUNT(*) as total_orders, SUM(total_amount) as total_sales, COUNT(DISTINCT session_id) as total_sessions FROM orders')
    result = cursor.fetchone()
    print(f"Total orders: {result[0]}")
    print(f"Total sales: {result[1]}")
    print(f"Total sessions: {result[2]}")
    
    # ตรวจสอบข้อมูลวันนี้ (ใช้วันที่ปัจจุบันของระบบ)
    today = datetime.now().date()
    print(f"\nToday's data ({today}):")
    cursor.execute("SELECT COUNT(*) as orders, SUM(total_amount) as sales, COUNT(DISTINCT session_id) as sessions FROM orders WHERE DATE(created_at, 'localtime') = ?", (today,))
    result = cursor.fetchone()
    print(f"Today orders: {result[0]}")
    print(f"Today sales: {result[1]}")
    print(f"Today sessions: {result[2]}")
    
    # ตรวจสอบข้อมูล 7 วันล่าสุด
    week_ago = today - timedelta(days=7)
    print(f"\n7 days data (from {week_ago}):")
    cursor.execute("SELECT COUNT(*) as orders, SUM(total_amount) as sales, COUNT(DISTINCT session_id) as sessions FROM orders WHERE DATE(created_at, 'localtime') >= ?", (week_ago,))
    result = cursor.fetchone()
    print(f"Week orders: {result[0]}")
    print(f"Week sales: {result[1]}")
    print(f"Week sessions: {result[2]}")
    
    # ตรวจสอบข้อมูล 30 วันล่าสุด
    month_ago = today - timedelta(days=30)
    print(f"\n30 days data (from {month_ago}):")
    cursor.execute("SELECT COUNT(*) as orders, SUM(total_amount) as sales, COUNT(DISTINCT session_id) as sessions FROM orders WHERE DATE(created_at, 'localtime') >= ?", (month_ago,))
    result = cursor.fetchone()
    print(f"Month orders: {result[0]}")
    print(f"Month sales: {result[1]}")
    print(f"Month sessions: {result[2]}")
    
    # ตรวจสอบข้อมูลตามวันที่ที่มีอยู่
    print("\nDates with orders:")
    cursor.execute("SELECT DATE(created_at, 'localtime') as order_date, COUNT(*) as orders, SUM(total_amount) as sales FROM orders GROUP BY DATE(created_at, 'localtime') ORDER BY order_date DESC LIMIT 10")
    for row in cursor.fetchall():
        print(f"Date: {row[0]}, Orders: {row[1]}, Sales: {row[2]}")
    
    conn.close()

if __name__ == "__main__":
    check_orders_table()