import sqlite3
from datetime import datetime

# เชื่อมต่อฐานข้อมูล
conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

# สร้างออเดอร์ทดสอบสำหรับวันนี้
today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print(f"กำลังสร้างออเดอร์ทดสอบสำหรับวันนี้: {today}")

# สร้างออเดอร์ใหม่
insert_order = """
    INSERT INTO orders (table_id, session_id, status, total_amount, created_at, updated_at, completed_at, bill_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""

session_id = f"test-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
order_data = (
    1,  # table_id
    session_id,  # session_id
    'completed',  # status
    150.0,  # total_amount
    today,  # created_at
    today,  # updated_at
    today,  # completed_at
    'checked'  # bill_status
)

try:
    cursor.execute(insert_order, order_data)
    order_id = cursor.lastrowid
    
    # Commit การเปลี่ยนแปลง
    conn.commit()
    
    print(f"สร้างออเดอร์ ID: {order_id} เรียบร้อยแล้ว")
    
    # ตรวจสอบออเดอร์ที่สร้างขึ้น
    check_query = """
        SELECT order_id, table_id, status, total_amount, created_at
        FROM orders 
        WHERE order_id = ?
    """
    
    cursor.execute(check_query, (order_id,))
    created_order = cursor.fetchone()
    
    if created_order:
        print(f"ยืนยันการสร้างออเดอร์:")
        print(f"Order ID: {created_order[0]}, โต๊ะ: {created_order[1]}, สถานะ: {created_order[2]}, ยอดรวม: {created_order[3]}, เวลา: {created_order[4]}")
    else:
        print("ไม่พบออเดอร์ที่สร้างขึ้น")
    
    # ตรวจสอบออเดอร์ในวันนี้ทั้งหมด
    today_check = """
        SELECT order_id, table_id, status, total_amount, created_at
        FROM orders 
        WHERE DATE(created_at) = DATE('now', 'localtime')
        ORDER BY created_at DESC
    """
    
    cursor.execute(today_check)
    today_orders = cursor.fetchall()
    
    print(f"\nออเดอร์ในวันนี้ทั้งหมด: {len(today_orders)} รายการ")
    for order in today_orders:
        print(f"Order ID: {order[0]}, โต๊ะ: {order[1]}, สถานะ: {order[2]}, ยอดรวม: {order[3]}, เวลา: {order[4]}")
        
except Exception as e:
    print(f"เกิดข้อผิดพลาด: {e}")
    conn.rollback()

conn.close()
print("\nเสร็จสิ้น!")