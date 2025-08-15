import sqlite3
import json
from datetime import datetime

def check_order_items_status():
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    # ดึงข้อมูลรายการอาหารสำหรับโต๊ะ 1 ในเซสชั่นปัจจุบัน
    query = """
    SELECT 
        oi.order_item_id,
        oi.order_id,
        oi.item_id,
        mi.name as menu_name,
        oi.quantity,
        oi.unit_price,
        oi.status as item_status,
        oi.customer_request,
        o.table_id,
        o.session_id,
        o.status as order_status,
        o.created_at
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN menu_items mi ON oi.item_id = mi.item_id
    WHERE o.table_id = 1
    ORDER BY o.created_at DESC, oi.order_item_id DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("=== รายการอาหารทั้งหมดสำหรับโต๊ะ 1 ===")
    print(f"{'ID':<5} {'เมนู':<20} {'จำนวน':<8} {'สถานะรายการ':<15} {'สถานะออเดอร์':<15} {'Session ID':<10}")
    print("-" * 80)
    
    current_session_items = []
    latest_session_id = None
    
    for row in results:
        order_item_id, order_id, item_id, menu_name, quantity, unit_price, item_status, customer_request, table_id, session_id, order_status, created_at = row
        
        if latest_session_id is None:
            latest_session_id = session_id
            
        if session_id == latest_session_id:
            current_session_items.append({
                'order_item_id': order_item_id,
                'menu_name': menu_name,
                'quantity': quantity,
                'item_status': item_status,
                'order_status': order_status,
                'session_id': session_id
            })
        
        print(f"{order_item_id:<5} {menu_name:<20} {quantity:<8} {item_status:<15} {order_status:<15} {session_id[:8] if session_id else 'None':<10}")
    
    print(f"\n=== เซสชั่นปัจจุบัน: {latest_session_id[:8] if latest_session_id else 'None'} ===")
    print("รายการในเซสชั่นปัจจุบัน:")
    
    status_count = {'pending': 0, 'accepted': 0, 'completed': 0, 'rejected': 0}
    
    for item in current_session_items:
        print(f"- {item['menu_name']} (จำนวน: {item['quantity']}) - สถานะ: {item['item_status']}")
        if item['item_status'] in status_count:
            status_count[item['item_status']] += 1
    
    print(f"\nสรุปสถานะในเซสชั่นปัจจุบัน:")
    print(f"- Pending: {status_count['pending']} รายการ")
    print(f"- Accepted: {status_count['accepted']} รายการ")
    print(f"- Completed: {status_count['completed']} รายการ")
    print(f"- Rejected: {status_count['rejected']} รายการ")
    
    # ตรวจสอบข้อมูลที่ API จะส่งกลับ
    print(f"\n=== ข้อมูลที่ API ควรส่งกลับสำหรับโต๊ะ 1 ===")
    api_query = """
    SELECT 
        o.order_id,
        mi.name as menu_name,
        oi.quantity,
        oi.unit_price as price,
        oi.status as item_status,
        oi.customer_request,
        o.session_id
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN menu_items mi ON oi.item_id = mi.item_id
    WHERE o.table_id = 1 AND o.session_id = ?
    ORDER BY oi.order_item_id
    """
    
    cursor.execute(api_query, (latest_session_id,))
    api_results = cursor.fetchall()
    
    print("ข้อมูลที่ API ส่งกลับ:")
    for row in api_results:
        order_id, menu_name, quantity, price, item_status, customer_request, session_id = row
        print(f"- {menu_name} x{quantity} - สถานะ: {item_status} - ราคา: ฿{price}")
    
    conn.close()
    
    return current_session_items, status_count

if __name__ == "__main__":
    check_order_items_status()