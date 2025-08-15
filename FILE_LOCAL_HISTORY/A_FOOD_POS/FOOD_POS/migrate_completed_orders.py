import sqlite3
from datetime import datetime

def migrate_completed_orders():
    """ย้ายข้อมูลออเดอร์ที่เสร็จสิ้นแล้วไปยัง order_history"""
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    try:
        # ดึงข้อมูลออเดอร์ที่เสร็จสิ้นแล้วที่ยังไม่อยู่ใน order_history
        cursor.execute('''
            SELECT o.order_id, o.table_id, o.session_id, o.status, o.total_amount, 
                   o.created_at, o.completed_at
            FROM orders o
            WHERE o.status = 'completed' 
            AND o.order_id NOT IN (SELECT order_id FROM order_history)
        ''')
        
        completed_orders = cursor.fetchall()
        print(f"พบออเดอร์ที่เสร็จสิ้นแล้ว {len(completed_orders)} รายการที่ต้องย้าย")
        
        for order_row in completed_orders:
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
            
            print(f"ย้ายออเดอร์ {order_id} พร้อม {len(order_items)} รายการอาหารเรียบร้อยแล้ว")
        
        conn.commit()
        print(f"\n✅ ย้ายข้อมูลเสร็จสิ้น! ย้ายออเดอร์ทั้งหมด {len(completed_orders)} รายการ")
        
        # ตรวจสอบผลลัพธ์
        cursor.execute('SELECT COUNT(*) FROM order_history')
        history_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM order_history_items')
        history_items_count = cursor.fetchone()[0]
        
        print(f"ตอนนี้มีข้อมูลใน order_history: {history_count} ออเดอร์")
        print(f"ตอนนี้มีข้อมูลใน order_history_items: {history_items_count} รายการ")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_completed_orders()