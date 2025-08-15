#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบง่าย ๆ เพื่อดู debug logs
"""

import requests
import json

def test_simple_notes():
    """ทดสอบง่าย ๆ สำหรับ notes"""
    print("🧪 ทดสอบง่าย ๆ สำหรับ notes")
    print("=" * 40)
    
    # ข้อมูลทดสอบ
    order_data = {
        "table_id": 99,
        "items": [
            {
                "item_id": 1,
                "quantity": 1,
                "notes": "ทดสอบ notes"
            }
        ]
    }
    
    print(f"📤 ส่งข้อมูล: {json.dumps(order_data, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/orders',
            json=order_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📨 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📨 Response: {json.dumps(result, ensure_ascii=False)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_simple_notes()