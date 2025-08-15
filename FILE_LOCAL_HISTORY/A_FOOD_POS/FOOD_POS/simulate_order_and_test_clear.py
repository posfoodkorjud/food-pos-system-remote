#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import uuid

def simulate_order_and_test_clear():
    """จำลองการสั่งอาหารและทดสอบการเคลียร์โต๊ะ"""
    base_url = "http://localhost:5000"
    table_id = 1  # ใช้โต๊ะ 1 ในการทดสอบ
    
    print("=== จำลองการสั่งอาหารและทดสอบการเคลียร์โต๊ะ ===")
    
    # 1. ตรวจสอบสถานะโต๊ะก่อน
    print(f"\n1. ตรวจสอบสถานะโต๊ะ {table_id} ก่อนสั่งอาหาร")
    response = requests.get(f"{base_url}/api/tables/{table_id}")
    if response.status_code == 200:
        table_data = response.json().get('data', {})
        print(f"สถานะ: {table_data.get('status')}")
        print(f"session_id: {table_data.get('session_id')}")
    
    # 2. สร้าง session ใหม่และสั่งอาหาร
    session_id = str(uuid.uuid4())
    print(f"\n2. สร้าง session ใหม่: {session_id}")
    
    # อัปเดตสถานะโต๊ะเป็น occupied
    update_data = {
        "status": "occupied",
        "session_id": session_id
    }
    response = requests.put(f"{base_url}/api/tables/{table_id}/status", json=update_data)
    print(f"อัปเดตสถานะโต๊ะ: {response.status_code}")
    
    # 3. สั่งอาหาร
    print("\n3. สั่งอาหาร")
    order_data = {
        "table_id": table_id,
        "session_id": session_id,
        "items": [
            {
                "menu_item_id": 1,
                "quantity": 2,
                "special_instructions": "ทดสอบ",
                "options": []
            }
        ]
    }
    response = requests.post(f"{base_url}/api/orders", json=order_data)
    print(f"สั่งอาหาร: {response.status_code}")
    if response.status_code == 200:
        order_result = response.json()
        print(f"Order ID: {order_result.get('order_id')}")
    
    # 4. ตรวจสอบสถานะโต๊ะหลังสั่งอาหาร
    print(f"\n4. ตรวจสอบสถานะโต๊ะ {table_id} หลังสั่งอาหาร")
    response = requests.get(f"{base_url}/api/tables/{table_id}")
    if response.status_code == 200:
        table_data = response.json().get('data', {})
        print(f"สถานะ: {table_data.get('status')}")
        print(f"session_id: {table_data.get('session_id')}")
    
    # 5. เปลี่ยนสถานะเป็น checkout (จำลองการชำระเงิน)
    print("\n5. เปลี่ยนสถานะเป็น checkout")
    update_data = {
        "status": "checkout",
        "session_id": session_id
    }
    response = requests.put(f"{base_url}/api/tables/{table_id}/status", json=update_data)
    print(f"อัปเดตสถานะ: {response.status_code}")
    
    # 6. ตรวจสอบสถานะโต๊ะก่อนเคลียร์
    print(f"\n6. ตรวจสอบสถานะโต๊ะ {table_id} ก่อนเคลียร์")
    response = requests.get(f"{base_url}/api/tables/{table_id}")
    if response.status_code == 200:
        table_data = response.json().get('data', {})
        print(f"สถานะ: {table_data.get('status')}")
        print(f"session_id: {table_data.get('session_id')}")
    
    # 7. ทดสอบการเคลียร์โต๊ะ
    print(f"\n7. ทดสอบการเคลียร์โต๊ะ {table_id}")
    response = requests.post(f"{base_url}/api/tables/{table_id}/clear")
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Old session_id: {result.get('old_session_id')}")
    
    # 8. ตรวจสอบสถานะโต๊ะหลังเคลียร์
    print(f"\n8. ตรวจสอบสถานะโต๊ะ {table_id} หลังเคลียร์")
    response = requests.get(f"{base_url}/api/tables/{table_id}")
    if response.status_code == 200:
        response_data = response.json()
        if 'data' in response_data:
            table_data = response_data['data']
            print(f"สถานะ: {table_data.get('status')}")
            print(f"session_id: {table_data.get('session_id')}")
            
            # ตรวจสอบว่าเคลียร์สำเร็จหรือไม่
            if table_data.get('status') == 'available' and table_data.get('session_id') is None:
                print("\n✅ การเคลียร์โต๊ะสำเร็จ!")
            else:
                print("\n❌ การเคลียร์โต๊ะไม่สำเร็จ!")
        else:
            print(f"Unexpected response: {response_data}")
    else:
        print(f"Error getting table status: {response.status_code}")

if __name__ == "__main__":
    simulate_order_and_test_clear()