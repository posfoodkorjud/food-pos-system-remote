#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import uuid

def setup_test_table():
    """ตั้งค่าโต๊ะสำหรับทดสอบปุ่มเคลียร์โต๊ะ"""
    base_url = "http://localhost:5000"
    table_id = 1  # ใช้โต๊ะ 1 ในการทดสอบ
    
    print("=== ตั้งค่าโต๊ะสำหรับทดสอบปุ่มเคลียร์โต๊ะ ===")
    
    # สร้าง session ใหม่
    session_id = str(uuid.uuid4())
    print(f"สร้าง session ใหม่: {session_id}")
    
    # ตั้งค่าโต๊ะให้มีสถานะ checkout (เพื่อให้ปุ่มเคลียร์โต๊ะแสดงขึ้น)
    print(f"\nตั้งค่าโต๊ะ {table_id} ให้มีสถานะ checkout")
    update_data = {
        "status": "checkout",
        "session_id": session_id
    }
    response = requests.put(f"{base_url}/api/tables/{table_id}/status", json=update_data)
    
    if response.status_code == 200:
        print("✅ ตั้งค่าสำเร็จ!")
        print(f"โต๊ะ {table_id} ตอนนี้มีสถานะ 'checkout' และควรแสดงปุ่มเคลียร์โต๊ะ")
        print("\nกรุณาไปที่หน้า admin และคลิกที่โต๊ะ 1 เพื่อทดสอบปุ่มเคลียร์โต๊ะ")
        
        # ตรวจสอบสถานะโต๊ะ
        response = requests.get(f"{base_url}/api/tables/{table_id}")
        if response.status_code == 200:
            table_data = response.json().get('data', {})
            print(f"\nสถานะปัจจุบัน: {table_data.get('status')}")
            print(f"session_id: {table_data.get('session_id')}")
    else:
        print(f"❌ เกิดข้อผิดพลาด: {response.status_code} - {response.text}")

if __name__ == "__main__":
    setup_test_table()