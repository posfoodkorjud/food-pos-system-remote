import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime
import time

# โหลดการตั้งค่า Google Sheets
with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# ตั้งค่า credentials
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
client = gspread.authorize(creds)

# เปิด Google Sheets
sheet = client.open_by_key(config['spreadsheet_id'])
worksheet = sheet.worksheet('Orders')

print("กำลังอ่านข้อมูลจาก Google Sheets...")

# อ่านข้อมูลทั้งหมด
all_data = worksheet.get_all_values()

if not all_data:
    print("ไม่พบข้อมูลใน Google Sheets")
    exit()

print(f"พบข้อมูลทั้งหมด {len(all_data)} แถว")

# แยกข้อมูลออกเป็นกลุ่ม Order
orders = {}
current_order = None

for i, row in enumerate(all_data[1:], 2):  # เริ่มจากแถว 2 (ข้าม header)
    if len(row) < 6:
        continue
        
    order_id = row[0].strip()
    
    # ตรวจสอบว่าเป็น Order ID ใหม่หรือไม่
    if order_id and order_id.isdigit():
        current_order = order_id
        if current_order not in orders:
            orders[current_order] = {
                'items': [],
                'summary': None,
                'first_row': i
            }
        
        # เพิ่มรายการสินค้า
        if len(row) >= 9:
            item_data = {
                'datetime': row[1],
                'item_name': row[2],
                'quantity': row[3],
                'unit_price': row[4],
                'total_price': row[5],
                'addon': row[6],
                'special_request': row[7],
                'status': row[8]
            }
            orders[current_order]['items'].append(item_data)
    
    # ตรวจสอบว่าเป็นแถวสรุปหรือไม่
    elif current_order and row[0].startswith('สรุป Order'):
        orders[current_order]['summary'] = {
            'total_items': row[2],
            'total_quantity': row[3],
            'total_amount': row[5] if len(row) > 5 else '0'
        }

print(f"พบ Order ทั้งหมด {len(orders)} รายการ")

# ล้างข้อมูลเก่า
print("กำลังล้างข้อมูลเก่า...")
worksheet.clear()

# รอสักครู่เพื่อหลีกเลี่ยง rate limit
time.sleep(2)

# สร้าง header ใหม่
header = [
    'Order ID', 'วันที่-เวลา', 'รายการอาหาร', 'จำนวน', 
    'ราคาต่อหน่วย (บาท)', 'ราคารวม (บาท)', 'เสริม', 
    'คำขอพิเศษ', 'สถานะ'
]

# เตรียมข้อมูลใหม่
new_data = [header]

# จัดเรียง Order ตามหมายเลข (ใหม่ไปเก่า)
sorted_orders = sorted(orders.items(), key=lambda x: int(x[0]), reverse=True)

for order_id, order_data in sorted_orders:
    # เพิ่มรายการสินค้าของแต่ละ Order
    for i, item in enumerate(order_data['items']):
        row_data = [
            order_id if i == 0 else '',  # แสดง Order ID เฉพาะแถวแรก
            item['datetime'],
            item['item_name'],
            item['quantity'],
            item['unit_price'],
            item['total_price'],
            item['addon'],
            item['special_request'],
            item['status']
        ]
        new_data.append(row_data)
    
    # เพิ่มแถวสรุป
    if order_data['summary']:
        summary_row = [
            f"สรุป Order {order_id}",
            '',
            order_data['summary']['total_items'],
            order_data['summary']['total_quantity'],
            '',
            order_data['summary']['total_amount'],
            '', '', ''
        ]
        new_data.append(summary_row)
    
    # เพิ่มแถวว่างเพื่อแยก Order
    new_data.append(['', '', '', '', '', '', '', '', ''])

print(f"กำลังเขียนข้อมูลใหม่ {len(new_data)} แถว...")

# เขียนข้อมูลใหม่ (ใช้ named arguments)
worksheet.update(values=new_data, range_name='A1')

print("\n=== การจัดระเบียบเสร็จสิ้น ===")
print(f"จัดระเบียบข้อมูล {len(orders)} Order เรียบร้อยแล้ว")
print(f"ข้อมูลทั้งหมด {len(new_data)} แถว (รวม header และแถวว่าง)")
print(f"URL: https://docs.google.com/spreadsheets/d/{config['spreadsheet_id']}")

# แสดงสรุป Order
print("\nสรุป Order ที่จัดระเบียบ (10 Order ล่าสุด):")
for order_id, order_data in sorted_orders[:10]:  # แสดง 10 Order แรก
    item_count = len(order_data['items'])
    total_amount = order_data['summary']['total_amount'] if order_data['summary'] else '0'
    print(f"Order {order_id}: {item_count} รายการ, รวม {total_amount} บาท")

if len(sorted_orders) > 10:
    print(f"... และอีก {len(sorted_orders) - 10} Order")

print("\nข้อมูลถูกจัดระเบียบแล้ว:")
print("- Order ID เรียงจากใหม่ไปเก่า")
print("- แต่ละ Order มีแถวสรุปและแถวว่างแยกกัน")
print("- Header ชัดเจนและเข้าใจง่าย")
print("- ข้อมูลไม่มีแถวว่างที่ไม่จำเป็น")