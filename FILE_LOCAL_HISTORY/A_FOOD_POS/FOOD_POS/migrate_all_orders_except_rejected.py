import sqlite3
from datetime import datetime

def migrate_all_orders_except_rejected():
    """ย้ายข้อมูลออเดอร์ทุกสถานะยกเว้น rejected จากตาราง orders ไปยัง order_history"""
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
        
        # แสดงรายละเอียดออเดอร์ที่จะย้าย
        print("\n=== รายการออเดอร์ที่จะย้าย ===")
        for order_row in orders_to_migrate:
            order_id, table_id, session_id, status, total_amount, created_at, completed_at = order_row
            print(f"Order {order_id}: โต๊ะ {table_id}, สถานะ {status}, ยอดรวม {total_amount} บาท")
        
        # ขอยืนยันจากผู้ใช้
        confirm = input("\nต้องการดำเนินการย้ายข้อมูลหรือไม่? (y/n): ")
        if confirm.lower() != 'y':
            print("ยกเลิกการย้ายข้อมูล")
            return
        
        migrated_count = 0
        
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
            print(f"ย้ายออเดอร์ {order_id} พร้อม {len(order_items)} รายการอาหารเรียบร้อยแล้ว")
        
        conn.commit()
        print(f"\n✅ ย้ายข้อมูลเสร็จสิ้น! ย้ายออเดอร์ทั้งหมด {migrated_count} รายการ")
        
        # ตรวจสอบผลลัพธ์
        cursor.execute('SELECT COUNT(*) FROM order_history')
        history_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM order_history_items')
        history_items_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM orders WHERE status != "rejected"')
        remaining_orders = cursor.fetchone()[0]
        
        print(f"\n=== สรุปผลลัพธ์ ===")
        print(f"ตอนนี้มีข้อมูลใน order_history: {history_count} ออเดอร์")
        print(f"ตอนนี้มีข้อมูลใน order_history_items: {history_items_count} รายการ")
        print(f"ออเดอร์ที่เหลือในตาราง orders (ยกเว้น rejected): {remaining_orders} รายการ")
        
        # แสดงออเดอร์ที่เหลือในตาราง orders
        cursor.execute('''
            SELECT order_id, status, total_amount, created_at
            FROM orders 
            WHERE status != 'rejected'
            ORDER BY order_id DESC
        ''')
        
        remaining_orders_list = cursor.fetchall()
        if remaining_orders_list:
            print("\n=== ออเดอร์ที่เหลือในตาราง orders ===")
            for order in remaining_orders_list:
                order_id, status, total_amount, created_at = order
                print(f"Order {order_id}: สถานะ {status}, ยอดรวม {total_amount} บาท, สร้างเมื่อ {created_at}")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_all_orders_except_rejected()