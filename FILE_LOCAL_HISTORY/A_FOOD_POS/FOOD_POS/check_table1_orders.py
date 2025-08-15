import sqlite3

def check_table1_orders():
    try:
        conn = sqlite3.connect('pos_database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("=== ตรวจสอบรายการอาหารในโต๊ะ 1 ===\n")
        
        # ตรวจสอบออเดอร์ทั้งหมดของโต๊ะ 1
        cursor.execute('''
            SELECT o.order_id, o.session_id, o.status as order_status, o.created_at,
                   oi.order_item_id, oi.status as item_status, oi.quantity, oi.unit_price,
                   mi.name as item_name
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN menu_items mi ON oi.item_id = mi.item_id
            WHERE o.table_id = 1
            ORDER BY o.order_id DESC, oi.order_item_id
        ''')
        
        results = cursor.fetchall()
        
        if not results:
            print("ไม่พบรายการอาหารในโต๊ะ 1")
            return
        
        current_order_id = None
        for row in results:
            if current_order_id != row['order_id']:
                current_order_id = row['order_id']
                print(f"\n📋 Order ID: {row['order_id']}")
                print(f"   Session ID: {row['session_id'][:8]}...")
                print(f"   Order Status: {row['order_status']}")
                print(f"   Created: {row['created_at']}")
                print(f"   รายการอาหาร:")
            
            status_emoji = {
                'pending': '⏳',
                'accepted': '✅', 
                'completed': '🟢',
                'rejected': '❌'
            }.get(row['item_status'], '❓')
            
            print(f"     {status_emoji} {row['item_name']} x{row['quantity']} - {row['item_status']} (Item ID: {row['order_item_id']})")
        
        # ตรวจสอบสถานะล่าสุดของโต๊ะ 1
        cursor.execute('''
            SELECT session_id, COUNT(*) as total_items,
                   SUM(CASE WHEN oi.status = 'pending' THEN 1 ELSE 0 END) as pending_count,
                   SUM(CASE WHEN oi.status = 'accepted' THEN 1 ELSE 0 END) as accepted_count,
                   SUM(CASE WHEN oi.status = 'completed' THEN 1 ELSE 0 END) as completed_count,
                   SUM(CASE WHEN oi.status = 'rejected' THEN 1 ELSE 0 END) as rejected_count
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.table_id = 1
            GROUP BY o.session_id
            ORDER BY MAX(o.order_id) DESC
            LIMIT 1
        ''')
        
        summary = cursor.fetchone()
        if summary:
            print(f"\n📊 สรุปสถานะล่าสุดของโต๊ะ 1:")
            print(f"   Session: {summary['session_id'][:8]}...")
            print(f"   รายการทั้งหมด: {summary['total_items']}")
            print(f"   ⏳ รอดำเนินการ: {summary['pending_count']}")
            print(f"   ✅ รับแล้ว: {summary['accepted_count']}")
            print(f"   🟢 เสร็จแล้ว: {summary['completed_count']}")
            print(f"   ❌ ปฏิเสธ: {summary['rejected_count']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == '__main__':
    check_table1_orders()