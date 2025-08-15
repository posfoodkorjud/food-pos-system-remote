import sqlite3
import json

def check_recent_orders():
    try:
        # เชื่อมต่อฐานข้อมูลที่ระบบใช้จริง
        conn = sqlite3.connect('backend/pos_database.db')
        cursor = conn.cursor()
        
        print("=== ตรวจสอบออเดอร์ล่าสุดใน pos_database.db ===")
        
        # ดูออเดอร์ล่าสุด 5 รายการ
        cursor.execute("""
            SELECT order_id, table_id, session_id, status, total_amount, created_at 
            FROM orders 
            ORDER BY order_id DESC 
            LIMIT 5
        """)
        
        orders = cursor.fetchall()
        print(f"\n📋 ออเดอร์ล่าสุด ({len(orders)} รายการ):")
        for order in orders:
            print(f"Order ID: {order[0]}, Table: {order[1]}, Session: {order[2][:8]}..., Status: {order[3]}, Total: {order[4]}฿, Time: {order[5]}")
        
        if orders:
            # ตรวจสอบ 2 ออเดอร์ล่าสุด
            for i in range(min(2, len(orders))):
                order_id = orders[i][0]
                print(f"\n🔍 รายละเอียดออเดอร์ {order_id}:")
                
                # ดูรายการอาหารในออเดอร์
                cursor.execute("""
                    SELECT oi.item_id, oi.quantity, oi.unit_price, oi.total_price, oi.customer_request,
                           m.name
                    FROM order_items oi
                    JOIN menu_items m ON oi.item_id = m.item_id
                    WHERE oi.order_id = ?
                    ORDER BY oi.order_item_id DESC
                """, (order_id,))
                
                items = cursor.fetchall()
                for item in items:
                    print(f"\n📝 รายการ: {item[5]} (ID: {item[0]})")
                    print(f"   จำนวน: {item[1]}")
                    print(f"   ราคาต่อหน่วย: {item[2]}฿")
                    print(f"   ราคารวม: {item[3]}฿")
                    print(f"   Special Request: '{item[4]}'")
                    
                    # วิเคราะห์ customer_request
                    if item[4]:
                        if '|' in item[4]:
                            parts = item[4].split('|')
                            print(f"   📊 แยกข้อมูล:")
                            if len(parts) >= 1 and parts[0].strip():
                                print(f"     - ตัวเลือกพิเศษ: '{parts[0].strip()}'")
                            if len(parts) >= 2 and parts[1].strip():
                                print(f"     - หมายเหตุ: '{parts[1].strip()}'")
                        else:
                            print(f"   📊 ข้อมูลเดียว: '{item[4]}'")
                    else:
                        print(f"   ⚠️ ไม่มี customer_request")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == '__main__':
    check_recent_orders()