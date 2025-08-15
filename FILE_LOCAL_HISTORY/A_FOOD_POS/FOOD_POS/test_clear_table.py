#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_clear_table():
    """ทดสอบการเคลียร์โต๊ะ"""
    base_url = "http://localhost:5000"
    
    # ดูข้อมูลโต๊ะทั้งหมดก่อน
    print("=== ข้อมูลโต๊ะก่อนเคลียร์ ===")
    response = requests.get(f"{base_url}/api/tables")
    if response.status_code == 200:
        tables = response.json()
        for table in tables:
            print(f"โต๊ะ {table['table_id']}: สถานะ={table['status']}, session_id={table.get('session_id', 'None')}")
    else:
        print(f"Error getting tables: {response.status_code}")
        return
    
    # หาโต๊ะที่มีสถานะไม่ใช่ available
    occupied_tables = [t for t in tables if t['status'] != 'available']
    
    if not occupied_tables:
        print("\nไม่มีโต๊ะที่ต้องเคลียร์")
        return
    
    # เลือกโต๊ะแรกที่ไม่ว่างมาทดสอบ
    test_table = occupied_tables[0]
    table_id = test_table['table_id']
    
    print(f"\n=== ทดสอบเคลียร์โต๊ะ {table_id} ===")
    print(f"สถานะก่อนเคลียร์: {test_table['status']}")
    print(f"session_id ก่อนเคลียร์: {test_table.get('session_id', 'None')}")
    
    # ส่งคำขอเคลียร์โต๊ะ
    response = requests.post(f"{base_url}/api/tables/{table_id}/clear")
    
    print(f"\nResponse status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Old session_id: {result.get('old_session_id')}")
        
        # ตรวจสอบสถานะโต๊ะหลังเคลียร์
        print("\n=== ตรวจสอบสถานะหลังเคลียร์ ===")
        response = requests.get(f"{base_url}/api/tables/{table_id}")
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {response_data}")
            if 'data' in response_data:
                updated_table = response_data['data']
                print(f"สถานะหลังเคลียร์: {updated_table['status']}")
                print(f"session_id หลังเคลียร์: {updated_table.get('session_id', 'None')}")
            elif 'status' in response_data:
                print(f"สถานะหลังเคลียร์: {response_data['status']}")
                print(f"session_id หลังเคลียร์: {response_data.get('session_id', 'None')}")
            else:
                print(f"Unexpected response format: {response_data}")
        else:
            print(f"Error getting updated table: {response.status_code} - {response.text}")
    else:
        print(f"Error clearing table: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_clear_table()