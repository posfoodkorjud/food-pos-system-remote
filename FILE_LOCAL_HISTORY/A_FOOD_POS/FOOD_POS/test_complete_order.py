#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบการส่งออเดอร์แบบสมบูรณ์ พร้อมตัวเลือกและหมายเหตุ
"""

import requests
import json
import sqlite3
import time

def test_complete_order():
    """ทดสอบส่งออเดอร์พร้อมตัวเลือกและหมายเหตุ"""
    print("🧪 ทดสอบส่งออเดอร์แบบสมบูรณ์")
    print("=" * 50)
    
    # ข้อมูลออเดอร์ที่มีทั้ง selected_option และ notes
    order_data = {
        "table_id": 99,
        "items": [
            {
                "item_id": 1,
                "quantity": 1,
                "selected_option": "หวานปกติ",
                "notes": "ไม่ใส่ผักชี"
            },
            {
                "item_id": 8,
                "quantity": 2,
                "selected_option": "เผ็ดน้อย",
                "notes": "ใส่ไข่ดาว 2 ฟอง"
            },
            {
                "item_id": 3,
                "quantity": 1,
                "notes": "ไม่ใส่หอม"
                # ไม่มี selected_option
            },
            {
                "item_id": 5,
                "quantity": 1,
                "selected_option": "หวานมาก"
                # ไม่มี notes
            }
        ]
    }
    
    print(f"📋 ข้อมูลที่ส่ง:")
    print(json.dumps(order_data, indent=2, ensure_ascii=False))
    print()
    
    try:
        # ส่งออเดอร์
        response = requests.post(
            'http://localhost:5000/api/orders',
            json=order_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📨 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📨 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            order_id = result.get('data', {}).get('order_id')
            if order_id:
                print(f"\n✅ ออเดอร์สำเร็จ! Order ID: {order_id}")
                
                # รอให้ฐานข้อมูลอัปเดต
                print("\n⏳ รอ 2 วินาที เพื่อให้ฐานข้อมูลอัปเดต...")
                time.sleep(2)
                
                # ตรวจสอบฐานข้อมูล
                check_order_in_database(order_id)
                
            else:
                print("❌ ไม่พบ order_id ใน response")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request Error: {e}")

def check_order_in_database(order_id):
    """ตรวจสอบออเดอร์ในฐานข้อมูล"""
    print(f"\n🔍 ตรวจสอบฐานข้อมูลสำหรับ Order ID: {order_id}")
    
    try:
        conn = sqlite3.connect('pos_database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # ตรวจสอบออเดอร์หลัก
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        order = cursor.fetchone()
        
        if order:
            print(f"✅ พบออเดอร์ในฐานข้อมูล:")
            print(f"   Order ID: {order['order_id']}")
            print(f"   Table ID: {order['table_id']}")
            print(f"   Status: {order['status']}")
            print(f"   Total Amount: {order['total_amount']}")
            
            # ตรวจสอบรายการอาหาร
            cursor.execute("""
                SELECT oi.*, mi.name as item_name 
                FROM order_items oi 
                JOIN menu_items mi ON oi.item_id = mi.item_id 
                WHERE oi.order_id = ?
                ORDER BY oi.order_item_id
            """, (order_id,))
            
            items = cursor.fetchall()
            print(f"\n📋 รายการอาหาร ({len(items)} รายการ):")
            
            for i, item in enumerate(items, 1):
                print(f"\n   {i}. {item['item_name']}")
                print(f"      Quantity: {item['quantity']}")
                print(f"      Unit Price: {item['unit_price']}")
                print(f"      Total Price: {item['total_price']}")
                print(f"      Customer Request: '{item['customer_request']}'")
                print(f"      Status: {item['status']}")
                
                # วิเคราะห์ customer request
                if item['customer_request']:
                    parts = item['customer_request'].split(' | ')
                    print(f"      Customer Request Parts: {parts}")
                else:
                    print(f"      ⚠️  Special Request ว่างเปล่า!")
                
        else:
            print(f"❌ ไม่พบออเดอร์ ID {order_id} ในฐานข้อมูล")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    test_complete_order()