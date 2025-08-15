#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

# เชื่อมต่อฐานข้อมูล
conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

# ดึงข้อมูล Order 170 จากฐานข้อมูล
cursor.execute('''
    SELECT oi.order_item_id, oi.order_id, mi.name, oi.quantity, oi.total_price, oi.created_at, oi.status
    FROM order_items oi 
    JOIN menu_items mi ON oi.item_id = mi.item_id 
    WHERE oi.order_id = 170 
    ORDER BY oi.created_at
''')

items = cursor.fetchall()

print(f'Order 170 ในฐานข้อมูล ({len(items)} รายการ):')
print('=' * 80)

for i, item in enumerate(items, 1):
    print(f'{i:2d}. {item[2]:<30} - จำนวน: {item[3]}, ราคา: {item[4]:>6}, สถานะ: {item[6]:<10}, เวลา: {item[5]}')

print('=' * 80)

# ตรวจสอบเฉพาะเมนู "น้ำเงาะ+เนื้อเงาะ"
print('\n🔍 ค้นหาเมนู "น้ำเงาะ+เนื้อเงาะ" ใน Order 170:')
rambutan_items = [item for item in items if 'น้ำเงาะ' in item[2]]

if rambutan_items:
    print(f'✅ พบเมนู "น้ำเงาะ+เนื้อเงาะ" จำนวน {len(rambutan_items)} รายการ:')
    for item in rambutan_items:
        print(f'   - {item[2]} (ID: {item[0]}) - ราคา: {item[4]} บาท, เวลา: {item[5]}, สถานะ: {item[6]}')
else:
    print('❌ ไม่พบเมนู "น้ำเงาะ+เนื้อเงาะ" ใน Order 170')

# ตรวจสอบยอดรวม
total = sum(item[4] for item in items)
print(f'\n💰 ยอดรวม Order 170: {total} บาท')

conn.close()