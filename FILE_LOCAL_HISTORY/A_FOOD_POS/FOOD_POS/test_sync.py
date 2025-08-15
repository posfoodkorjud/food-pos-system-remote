#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ทดสอบการซิงค์ Google Sheets
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.new_google_sheets_sync import sync_order_to_new_format
from datetime import datetime

# ข้อมูลทดสอบ
order_data = {
    'order_id': 172,
    'table_id': 4,
    'session_id': 'test-session-123',
    'status': 'รอดำเนินการ',
    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

order_items = [
    {
        'item_name': 'ข้าวผัดกุ้ง',
        'quantity': 1,
        'unit_price': 45.0,
        'total_price': 45.0,
        'customer_request': 'ไม่เผ็ด',
        'special_options': ''
    },
    {
        'item_name': 'น้ำส้ม',
        'quantity': 2,
        'unit_price': 25.0,
        'total_price': 50.0,
        'customer_request': '',
        'special_options': ''
    }
]

print("[TEST] เริ่มทดสอบการซิงค์ Google Sheets...")
print(f"[TEST] Order ID: {order_data['order_id']}")
print(f"[TEST] Items: {len(order_items)} รายการ")

try:
    result = sync_order_to_new_format(order_data, order_items)
    if result:
        print("[TEST] ✅ การซิงค์สำเร็จ!")
    else:
        print("[TEST] ❌ การซิงค์ล้มเหลว")
except Exception as e:
    print(f"[TEST] ❌ เกิดข้อผิดพลาด: {e}")
    import traceback
    traceback.print_exc()