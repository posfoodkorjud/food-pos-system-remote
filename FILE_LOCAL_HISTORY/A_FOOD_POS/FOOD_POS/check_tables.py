import sqlite3

def check_database_tables():
    try:
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ดูตารางทั้งหมด
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print("ตารางทั้งหมดในฐานข้อมูล:")
        for table in tables:
            print(f"- {table[0]}")
        
        print("\n=== ตรวจสอบตารางที่เกี่ยวข้องกับ order ===")
        
        # ตรวจสอบตาราง orders
        if any('orders' in table[0] for table in tables):
            cursor.execute("SELECT COUNT(*) FROM orders")
            order_count = cursor.fetchone()[0]
            print(f"ตาราง orders: มี {order_count} รายการ")
            
            # ดูข้อมูลตัวอย่าง
            cursor.execute("SELECT order_id, table_id, status, created_at FROM orders ORDER BY order_id DESC LIMIT 3")
            recent_orders = cursor.fetchall()
            print("ออเดอร์ล่าสุด 3 รายการ:")
            for order in recent_orders:
                print(f"  - Order ID: {order[0]}, Table: {order[1]}, Status: {order[2]}, Created: {order[3]}")
        
        # ตรวจสอบตาราง order_items
        if any('order_items' in table[0] for table in tables):
            cursor.execute("SELECT COUNT(*) FROM order_items")
            item_count = cursor.fetchone()[0]
            print(f"\nตาราง order_items: มี {item_count} รายการ")
        
        # ตรวจสอบว่ามีตาราง order_history หรือไม่
        order_history_exists = any('order_history' in table[0] for table in tables)
        print(f"\nตาราง order_history: {'มี' if order_history_exists else 'ไม่มี'}")
        
        conn.close()
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    check_database_tables()