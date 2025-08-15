import sqlite3

def check_order_data():
    try:
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ตรวจสอบข้อมูลออเดอร์ล่าสุด 5 รายการ
        cursor.execute("""
            SELECT o.order_id, o.table_id, o.session_id, o.status, 
                   o.created_at, o.completed_at, o.total_amount,
                   t.table_name, t.created_at as session_created_at, t.checkout_at
            FROM orders o
            LEFT JOIN tables t ON o.table_id = t.table_id
            ORDER BY o.order_id DESC
            LIMIT 5
        """)
        
        orders = cursor.fetchall()
        print("Recent orders with table data:")
        print("=" * 80)
        for order in orders:
            print(f"Order ID: {order[0]}")
            print(f"Table ID: {order[1]}")
            print(f"Table Name: {order[7]}")
            print(f"Session Created: {order[8]}")
            print(f"Checkout At: {order[9]}")
            print("-" * 40)
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_order_data()