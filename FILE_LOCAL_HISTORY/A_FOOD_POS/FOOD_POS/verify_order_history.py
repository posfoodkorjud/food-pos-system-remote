import sqlite3
from datetime import datetime

def verify_order_history():
    """ตรวจสอบข้อมูลใน order_history และเปรียบเทียบกับ orders"""
    conn = sqlite3.connect('pos_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        print("=== ตรวจสอบข้อมูลใน order_history ===")
        
        # ตรวจสอบจำนวนออเดอร์ทั้งหมดใน order_history
        cursor.execute("SELECT COUNT(*) FROM order_history")
        total_history = cursor.fetchone()[0]
        print(f"📊 จำนวนออเดอร์ทั้งหมดใน order_history: {total_history} รายการ")
        
        # ตรวจสอบออเดอร์วันนี้ใน order_history
        cursor.execute("""
            SELECT COUNT(*) FROM order_history 
            WHERE DATE(created_at) = DATE('now', 'localtime')
        """)
        today_history = cursor.fetchone()[0]
        print(f"🗓️ ออเดอร์วันนี้ใน order_history: {today_history} รายการ")
        
        # แสดงออเดอร์วันนี้ใน order_history
        cursor.execute("""
            SELECT order_id, table_id, status, total_amount, created_at, completed_at
            FROM order_history 
            WHERE DATE(created_at) = DATE('now', 'localtime')
            ORDER BY created_at DESC
        """)
        
        today_orders = cursor.fetchall()
        if today_orders:
            print("\n📋 รายละเอียดออเดอร์วันนี้ใน order_history:")
            for order in today_orders:
                completed_status = "เสร็จแล้ว" if order['completed_at'] else "ยังไม่เสร็จ"
                print(f"  Order {order['order_id']}: โต๊ะ {order['table_id']}, สถานะ {order['status']}, ยอดรวม {order['total_amount']} บาท, {completed_status}")
        
        print("\n=== เปรียบเทียบกับตาราง orders ===")
        
        # ตรวจสอบออเดอร์วันนี้ใน orders
        cursor.execute("""
            SELECT COUNT(*) FROM orders 
            WHERE DATE(created_at) = DATE('now', 'localtime')
        """)
        today_orders_count = cursor.fetchone()[0]
        print(f"🗓️ ออเดอร์วันนี้ใน orders: {today_orders_count} รายการ")
        
        # แสดงออเดอร์วันนี้ใน orders
        cursor.execute("""
            SELECT order_id, table_id, status, total_amount, created_at, completed_at
            FROM orders 
            WHERE DATE(created_at) = DATE('now', 'localtime')
            ORDER BY created_at DESC
        """)
        
        orders_today = cursor.fetchall()
        if orders_today:
            print("\n📋 รายละเอียดออเดอร์วันนี้ใน orders:")
            for order in orders_today:
                completed_status = "เสร็จแล้ว" if order['completed_at'] else "ยังไม่เสร็จ"
                print(f"  Order {order['order_id']}: โต๊ะ {order['table_id']}, สถานะ {order['status']}, ยอดรวม {order['total_amount']} บาท, {completed_status}")
        
        # ตรวจสอบออเดอร์ที่อยู่ในทั้งสองตาราง
        cursor.execute("""
            SELECT o.order_id, o.status as orders_status, h.status as history_status
            FROM orders o
            INNER JOIN order_history h ON o.order_id = h.order_id
            WHERE DATE(o.created_at) = DATE('now', 'localtime')
        """)
        
        duplicate_orders = cursor.fetchall()
        if duplicate_orders:
            print("\n⚠️ ออเดอร์ที่อยู่ในทั้งสองตาราง:")
            for order in duplicate_orders:
                print(f"  Order {order['order_id']}: orders={order['orders_status']}, history={order['history_status']}")
        
        # ตรวจสอบการทำงานของ API order-history
        print("\n=== ทดสอบ API order-history ===")
        cursor.execute("""
            SELECT oh.order_id, oh.table_id, oh.session_id, 
                   oh.status, oh.created_at, oh.completed_at, oh.total_amount
            FROM order_history oh
            WHERE DATE(oh.created_at) = DATE('now', 'localtime')
            ORDER BY oh.created_at DESC
        """)
        
        api_result = cursor.fetchall()
        if api_result:
            print(f"✅ API จะส่งคืน {len(api_result)} ออเดอร์สำหรับวันนี้:")
            for order in api_result:
                print(f"  Order {order['order_id']}: โต๊ะ {order['table_id']}, ยอดรวม {order['total_amount']} บาท")
        else:
            print("❌ API จะไม่ส่งคืนออเดอร์ใดๆ สำหรับวันนี้")
        
        print("\n=== สรุป ===")
        if today_history > 0:
            print("✅ ออเดอร์วันนี้ถูกย้ายไปยัง order_history แล้ว")
            print("✅ หน้าประวัติคำสั่งซื้อจะแสดงออเดอร์วันนี้")
        else:
            print("❌ ยังไม่มีออเดอร์วันนี้ใน order_history")
            print("❌ หน้าประวัติคำสั่งซื้อจะไม่แสดงออเดอร์วันนี้")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_order_history()