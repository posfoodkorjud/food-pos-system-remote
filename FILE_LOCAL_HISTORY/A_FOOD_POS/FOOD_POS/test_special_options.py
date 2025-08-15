import requests
import json
import time
import sqlite3

def test_order_with_special_options():
    base_url = "http://localhost:5000"
    
    # ข้อมูลออเดอร์ทดสอบพร้อมตัวเลือกพิเศษ
    order_data = {
        "table_id": 99,
        "items": [
            {
                "item_id": 1,  # ข้าวผัด
                "quantity": 1,
                "selected_option": "หวานปกติ",  # ตัวเลือกพิเศษ
                "notes": "ไม่ใส่ผักชี"  # หมายเหตุ
            },
            {
                "item_id": 8,  # ข้าวกะเพราทะเล
                "quantity": 1,
                "selected_option": "เผ็ดน้อย",  # ตัวเลือกพิเศษ
                "notes": "ใส่ไข่ดาว"  # หมายเหตุ
            }
        ]
    }
    
    print("🧪 ทดสอบส่งออเดอร์พร้อมตัวเลือกพิเศษ")
    print(f"📤 ข้อมูลที่ส่ง: {json.dumps(order_data, ensure_ascii=False, indent=2)}")
    
    try:
        # ส่งออเดอร์
        response = requests.post(f"{base_url}/api/orders", json=order_data)
        print(f"\n📨 Response Status: {response.status_code}")
        print(f"📨 Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            order_id = result.get('order_id')
            print(f"\n✅ ออเดอร์สำเร็จ! Order ID: {order_id}")
            
            # รอสักครู่แล้วตรวจสอบฐานข้อมูล
            time.sleep(1)
            check_database_for_order(order_id)
        else:
            print(f"\n❌ ส่งออเดอร์ไม่สำเร็จ: {response.status_code}")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

def check_database_for_order(order_id):
    print(f"\n🔍 ตรวจสอบฐานข้อมูลสำหรับ Order ID: {order_id}")
    
    try:
        conn = sqlite3.connect('backend/pos_database.db')
        cursor = conn.cursor()
        
        # ตรวจสอบออเดอร์
        cursor.execute("""
            SELECT order_id, table_id, status, total_amount, created_at 
            FROM orders 
            WHERE order_id = ?
        """, (order_id,))
        
        order = cursor.fetchone()
        if order:
            print(f"📋 ออเดอร์: ID={order[0]}, Table={order[1]}, Status={order[2]}, Total={order[3]}฿, Time={order[4]}")
            
            # ตรวจสอบรายการอาหาร
            cursor.execute("""
                SELECT oi.item_id, oi.quantity, oi.unit_price, oi.total_price, oi.customer_request,
                       m.name
                FROM order_items oi
                JOIN menu_items m ON oi.item_id = m.item_id
                WHERE oi.order_id = ?
                ORDER BY oi.order_item_id
            """, (order_id,))
            
            items = cursor.fetchall()
            print(f"\n📝 รายการอาหาร ({len(items)} รายการ):")
            
            for i, item in enumerate(items, 1):
                print(f"\n{i}. {item[5]} (ID: {item[0]})")
                print(f"   จำนวน: {item[1]}")
                print(f"   ราคาต่อหน่วย: {item[2]}฿")
                print(f"   ราคารวม: {item[3]}฿")
                print(f"   Customer Request: '{item[4]}'")
                
                # วิเคราะห์ customer_request
                if item[4]:
                    if '|' in item[4]:
                        parts = item[4].split('|')
                        print(f"   📊 แยกข้อมูล:")
                        if len(parts) >= 1 and parts[0].strip():
                            print(f"     ✅ ตัวเลือกพิเศษ: '{parts[0].strip()}'")
                        if len(parts) >= 2 and parts[1].strip():
                            print(f"     ✅ หมายเหตุ: '{parts[1].strip()}'")
                    else:
                        print(f"   📊 ข้อมูลเดียว: '{item[4]}'")
                else:
                    print(f"   ❌ ไม่มี customer_request (ข้อมูลสูญหาย!)")
        else:
            print(f"❌ ไม่พบออเดอร์ ID {order_id} ในฐานข้อมูล")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการตรวจสอบฐานข้อมูล: {e}")

if __name__ == '__main__':
    test_order_with_special_options()