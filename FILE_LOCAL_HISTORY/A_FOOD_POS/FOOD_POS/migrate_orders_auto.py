import sqlite3
from datetime import datetime

def migrate_all_orders_except_rejected_auto():
    """ย้ายข้อมูลออเดอร์ทุกสถานะยกเว้น rejected จากตาราง orders ไปยัง order_history (อัตโนมัติ)"""
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    try:
        # ดึงข้อมูลออเดอร์ทุกสถานะยกเว้น rejected ที่ยังไม่อยู่ใน order_history
        cursor.execute('''
            SELECT o.order_id, o.table_id, o.session_id, o.status, o.total_amount, 
                   o.created_at, o.completed_at
            FROM orders o
            WHERE o.status != 'rejected' 
            AND o.order_id NOT IN (SELECT order_id FROM order_history)
        ''')
        
        orders_to_migrate = cursor.fetchall()
        print(f"พบออเดอร์ที่ต้องย้าย {len(orders_to_migrate)} รายการ (ยกเว้น rejected)")
        
        if len(orders_to_migrate) == 0:
            print("ไม่มีออเดอร์ที่ต้องย้าย")
            return
        
        # แสดงรายละเอียดออเดอร์ที่จะย้าย (แค่ 10 รายการแรก)
        print("\n=== รายการออเดอร์ที่จะย้าย (แสดง 10 รายการแรก) ===")
        for i, order_row in enumerate(orders_to_migrate[:10]):
            order_id, table_id, session_id, status, total_amount, created_at, completed_at = order_row
            print(f"Order {order_id}: โต๊ะ {table_id}, สถานะ {status}, ยอดรวม {total_amount} บาท")
        
        if len(orders_to_migrate) > 10:
            print(f"... และอีก {len(orders_to_migrate) - 10} รายการ")
        
        print("\n🔄 เริ่มการย้ายข้อมูล...")
        
        migrated_count = 0
        total_items = 0
        
        for order_row in orders_to_migrate:
            order_id = order_row[0]
            
            # ย้ายข้อมูลออเดอร์ไปยัง order_history
            cursor.execute('''
                INSERT INTO order_history (order_id, table_id, session_id, status, total_amount, 
                                          created_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', order_row)
            
            # ดึงรายการอาหารในออเดอร์
            cursor.execute('''
                SELECT oi.order_id, oi.item_id, oi.quantity, oi.unit_price, oi.customer_request
                FROM order_items oi
                WHERE oi.order_id = ?
            ''', (order_id,))
            
            order_items = cursor.fetchall()
            
            # ย้ายรายการอาหารไปยัง order_history_items
            for item_row in order_items:
                cursor.execute('''
                    INSERT INTO order_history_items (order_id, menu_item_id, quantity, price, customer_request)
                    VALUES (?, ?, ?, ?, ?)
                ''', item_row)
            
            migrated_count += 1
            total_items += len(order_items)
            
            # แสดงความคืบหน้าทุก 10 ออเดอร์
            if migrated_count % 10 == 0:
                print(f"ย้ายแล้ว {migrated_count}/{len(orders_to_migrate)} ออเดอร์")
        
        conn.commit()
        print(f"\n✅ ย้ายข้อมูลเสร็จสิ้น!")
        print(f"📊 ย้ายออเดอร์ทั้งหมด: {migrated_count} รายการ")
        print(f"🍽️ ย้ายรายการอาหารทั้งหมด: {total_items} รายการ")
        
        # ตรวจสอบผลลัพธ์
        cursor.execute('SELECT COUNT(*) FROM order_history')
        history_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM order_history_items')
        history_items_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM orders WHERE status != "rejected"')
        remaining_orders = cursor.fetchone()[0]
        
        print(f"\n=== สรุปผลลัพธ์ ===")
        print(f"📈 ข้อมูลใน order_history: {history_count} ออเดอร์")
        print(f"📈 ข้อมูลใน order_history_items: {history_items_count} รายการ")
        print(f"📉 ออเดอร์ที่เหลือในตาราง orders (ยกเว้น rejected): {remaining_orders} รายการ")
        
        # แสดงออเดอร์ที่เหลือในตาราง orders (ถ้ามี)
        if remaining_orders > 0:
            cursor.execute('''
                SELECT order_id, status, total_amount, created_at
                FROM orders 
                WHERE status != 'rejected'
                ORDER BY order_id DESC
                LIMIT 10
            ''')
            
            remaining_orders_list = cursor.fetchall()
            print("\n=== ออเดอร์ที่เหลือในตาราง orders (แสดง 10 รายการล่าสุด) ===")
            for order in remaining_orders_list:
                order_id, status, total_amount, created_at = order
                print(f"Order {order_id}: สถานะ {status}, ยอดรวม {total_amount} บาท, สร้างเมื่อ {created_at}")
        
        # ตรวจสอบออเดอร์วันนี้ใน order_history
        cursor.execute('''
            SELECT COUNT(*) FROM order_history 
            WHERE DATE(created_at) = DATE('now', 'localtime')
        ''')
        today_history_count = cursor.fetchone()[0]
        print(f"\n🗓️ ออเดอร์วันนี้ใน order_history: {today_history_count} รายการ")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_all_orders_except_rejected_auto()