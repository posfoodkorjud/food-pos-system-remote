import sqlite3
import datetime

def check_today_orders():
    conn = sqlite3.connect('pos_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # ตรวจสอบจำนวนออเดอร์วันนี้ในตาราง orders
    cursor.execute("SELECT COUNT(*) FROM orders WHERE DATE(created_at) = DATE('now', 'localtime')")
    orders_today = cursor.fetchone()[0]
    print(f'Orders in orders table today: {orders_today}')
    
    # ตรวจสอบจำนวนออเดอร์วันนี้ในตาราง order_history
    cursor.execute("SELECT COUNT(*) FROM order_history WHERE DATE(created_at) = DATE('now', 'localtime')")
    history_today = cursor.fetchone()[0]
    print(f'Orders in order_history table today: {history_today}')
    
    # ตรวจสอบออเดอร์ล่าสุดในตาราง orders
    cursor.execute("""
        SELECT order_id, status, total_amount, created_at 
        FROM orders 
        WHERE DATE(created_at) = DATE('now', 'localtime') 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    orders = cursor.fetchall()
    print('\nRecent orders in orders table today:')
    for order in orders:
        print(f'Order {order[0]}: status={order[1]}, amount={order[2]}, created_at={order[3]}')
    
    # ตรวจสอบออเดอร์ล่าสุดในตาราง order_history
    cursor.execute("""
        SELECT order_id, status, total_amount, created_at 
        FROM order_history 
        WHERE DATE(created_at) = DATE('now', 'localtime') 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    history_orders = cursor.fetchall()
    print('\nRecent orders in order_history table today:')
    for order in history_orders:
        print(f'Order {order[0]}: status={order[1]}, amount={order[2]}, created_at={order[3]}')
    
    # ตรวจสอบสถานะของออเดอร์วันนี้
    cursor.execute("""
        SELECT status, COUNT(*) as count, SUM(total_amount) as total
        FROM orders 
        WHERE DATE(created_at) = DATE('now', 'localtime')
        GROUP BY status
    """)
    status_summary = cursor.fetchall()
    print('\nOrder status summary for today (orders table):')
    for row in status_summary:
        print(f'Status {row[0]}: {row[1]} orders, total: {row[2]} baht')
    
    conn.close()

if __name__ == '__main__':
    check_today_orders()