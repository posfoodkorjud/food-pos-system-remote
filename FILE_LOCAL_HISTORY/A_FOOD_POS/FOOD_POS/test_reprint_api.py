import sqlite3
import json
from datetime import datetime

def test_reprint_api():
    try:
        # เชื่อมต่อฐานข้อมูล
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ดึงข้อมูลออเดอร์ล่าสุด 3 รายการ
        query = """
        SELECT 
            o.order_id,
            o.table_id,
            o.total_amount,
            o.created_at,
            t.table_name,
            t.created_at as session_created_at,
            t.checkout_at
        FROM orders o
        LEFT JOIN tables t ON o.table_id = t.table_id
        ORDER BY o.order_id DESC
        LIMIT 3
        """
        
        cursor.execute(query)
        orders = cursor.fetchall()
        
        print("=== ข้อมูลออเดอร์สำหรับทดสอบ reprintReceipt ===")
        print()
        
        for order in orders:
            order_id, table_id, total_amount, created_at, table_name, session_created_at, checkout_at = order
            
            print(f"Order ID: {order_id}")
            print(f"Table ID: {table_id}")
            print(f"Table Name: {table_name}")
            print(f"Total Amount: {total_amount}")
            print(f"Order Created: {created_at}")
            print(f"Session Created At: {session_created_at}")
            print(f"Checkout At: {checkout_at}")
            
            # จำลองข้อมูลที่ API จะส่งกลับ
            api_response = {
                "success": True,
                "data": {
                    "id": order_id,
                    "table_id": table_id,
                    "table_name": table_name,
                    "total_amount": total_amount,
                    "created_at": created_at,
                    "session_created_at": session_created_at,
                    "checkout_at": checkout_at,
                    "items": []
                }
            }
            
            print("\n--- API Response Simulation ---")
            print(json.dumps(api_response, indent=2, ensure_ascii=False))
            
            # ตรวจสอบว่าข้อมูลเวลามีหรือไม่
            if session_created_at:
                try:
                    arrival_time = datetime.fromisoformat(session_created_at.replace('Z', '+00:00'))
                    print(f"\n✅ เวลาที่มาถึง: {arrival_time.strftime('%d/%m/%Y %H:%M:%S')}")
                except Exception as e:
                    print(f"\n❌ Error formatting arrival time: {e}")
            else:
                print("\n❌ ไม่มีข้อมูลเวลาที่มาถึง")
                
            if checkout_at:
                try:
                    checkout_time = datetime.fromisoformat(checkout_at.replace('Z', '+00:00'))
                    print(f"✅ เวลาเช็คบิล: {checkout_time.strftime('%d/%m/%Y %H:%M:%S')}")
                except Exception as e:
                    print(f"❌ Error formatting checkout time: {e}")
            else:
                print("❌ ไม่มีข้อมูลเวลาเช็คบิล")
                
            print("\n" + "="*50 + "\n")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_reprint_api()