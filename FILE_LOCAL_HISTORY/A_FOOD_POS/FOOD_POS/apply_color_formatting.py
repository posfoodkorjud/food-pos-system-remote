import sqlite3
import json
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime
from collections import defaultdict
import time

# โหลดการตั้งค่า
with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# เชื่อมต่อ Google Sheets
creds = Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
client = gspread.authorize(creds)
sheet = client.open_by_key(config['spreadsheet_id']).worksheet('Orders')

# เชื่อมต่อฐานข้อมูล
conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

print("🎨 กำลังใช้การจัดรูปแบบสีสำหรับ Google Sheets...")

# ดึงข้อมูล Order IDs ที่มีอยู่
cursor.execute('''
    SELECT DISTINCT o.order_id
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'completed'
    ORDER BY o.order_id DESC
''')

order_ids = [row[0] for row in cursor.fetchall()]
print(f"📊 พบ {len(order_ids)} Orders ที่ต้องจัดสี")

# กำหนดชุดสีสำหรับแต่ละ Order (สีอ่อนและสีเข้ม)
color_sets = [
    # ชุดสีส้ม
    {
        'light': {'red': 1.0, 'green': 0.9, 'blue': 0.8},    # ส้มอ่อน
        'dark': {'red': 1.0, 'green': 0.7, 'blue': 0.4}      # ส้มเข้ม
    },
    # ชุดสีเขียว
    {
        'light': {'red': 0.8, 'green': 1.0, 'blue': 0.8},    # เขียวอ่อน
        'dark': {'red': 0.6, 'green': 0.9, 'blue': 0.6}      # เขียวเข้ม
    },
    # ชุดสีฟ้า
    {
        'light': {'red': 0.8, 'green': 0.9, 'blue': 1.0},    # ฟ้าอ่อน
        'dark': {'red': 0.6, 'green': 0.8, 'blue': 1.0}      # ฟ้าเข้ม
    },
    # ชุดสีม่วง
    {
        'light': {'red': 0.95, 'green': 0.8, 'blue': 1.0},   # ม่วงอ่อน
        'dark': {'red': 0.9, 'green': 0.6, 'blue': 1.0}      # ม่วงเข้ม
    },
    # ชุดสีชมพู
    {
        'light': {'red': 1.0, 'green': 0.9, 'blue': 0.95},   # ชมพูอ่อน
        'dark': {'red': 1.0, 'green': 0.7, 'blue': 0.8}      # ชมพูเข้ม
    },
    # ชุดสีเหลือง
    {
        'light': {'red': 1.0, 'green': 1.0, 'blue': 0.8},    # เหลืองอ่อน
        'dark': {'red': 1.0, 'green': 0.9, 'blue': 0.5}      # เหลืองเข้ม
    }
]

# กำหนดสีให้แต่ละ Order
order_colors = {}
for i, order_id in enumerate(order_ids):
    order_colors[order_id] = color_sets[i % len(color_sets)]

print(f"🎯 กำหนดสีให้ {len(order_colors)} Orders แล้ว")

# ดึงข้อมูลทั้งหมดจาก Google Sheets
all_values = sheet.get_all_values()
print(f"📋 พบข้อมูลใน Google Sheets: {len(all_values)} แถว")

# สร้าง batch requests สำหรับการจัดสี
batch_requests = []
current_order_id = None

for i, row in enumerate(all_values[1:], start=2):  # เริ่มจากแถว 2 (ข้าม header)
    if len(row) > 0 and row[0]:
        # ตรวจสอบว่าเป็นแถวสรุปหรือไม่
        if row[0].startswith('สรุป Order'):
            # แยก Order ID จากข้อความสรุป
            try:
                order_id = int(row[0].replace('สรุป Order ', ''))
                if order_id in order_colors:
                    # จัดรูปแบบแถวสรุปยอด (สีเข้ม)
                    batch_requests.append({
                        'repeatCell': {
                            'range': {
                                'sheetId': sheet.id,
                                'startRowIndex': i-1,
                                'endRowIndex': i,
                                'startColumnIndex': 0,
                                'endColumnIndex': 9
                            },
                            'cell': {
                                'userEnteredFormat': {
                                    'backgroundColor': order_colors[order_id]['dark'],
                                    'textFormat': {
                                        'bold': True,
                                        'fontSize': 11
                                    },
                                    'horizontalAlignment': 'CENTER'
                                }
                            },
                            'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
                        }
                    })
            except ValueError:
                pass
        else:
            # แถวข้อมูลสินค้า - ดึง Order ID จากคอลัมน์แรก
            try:
                order_id = int(row[0])
                current_order_id = order_id
                if order_id in order_colors:
                    # จัดรูปแบบแถวข้อมูล (สีอ่อน)
                    batch_requests.append({
                        'repeatCell': {
                            'range': {
                                'sheetId': sheet.id,
                                'startRowIndex': i-1,
                                'endRowIndex': i,
                                'startColumnIndex': 0,
                                'endColumnIndex': 9
                            },
                            'cell': {
                                'userEnteredFormat': {
                                    'backgroundColor': order_colors[order_id]['light']
                                }
                            },
                            'fields': 'userEnteredFormat.backgroundColor'
                        }
                    })
            except ValueError:
                # ถ้าไม่สามารถแปลงเป็น int ได้ ใช้สีของ Order ปัจจุบัน
                if current_order_id and current_order_id in order_colors:
                    batch_requests.append({
                        'repeatCell': {
                            'range': {
                                'sheetId': sheet.id,
                                'startRowIndex': i-1,
                                'endRowIndex': i,
                                'startColumnIndex': 0,
                                'endColumnIndex': 9
                            },
                            'cell': {
                                'userEnteredFormat': {
                                    'backgroundColor': order_colors[current_order_id]['light']
                                }
                            },
                            'fields': 'userEnteredFormat.backgroundColor'
                        }
                    })

print(f"🔧 เตรียม batch requests: {len(batch_requests)} รายการ")

# ส่ง batch requests แบบแบ่งเป็นกลุ่มเพื่อหลีกเลี่ยง quota limit
batch_size = 50  # ลดขนาด batch เพื่อหลีกเลี่ยง quota limit
total_batches = (len(batch_requests) + batch_size - 1) // batch_size

for i in range(0, len(batch_requests), batch_size):
    batch = batch_requests[i:i+batch_size]
    batch_num = (i // batch_size) + 1
    
    print(f"📤 ส่ง batch {batch_num}/{total_batches} ({len(batch)} requests)...")
    
    try:
        sheet.spreadsheet.batch_update({'requests': batch})
        print(f"✅ Batch {batch_num} สำเร็จ")
        
        # รอสักครู่เพื่อหลีกเลี่ยง rate limit
        if i + batch_size < len(batch_requests):
            print("⏳ รอ 2 วินาทีเพื่อหลีกเลี่ยง rate limit...")
            time.sleep(2)
            
    except Exception as e:
        print(f"⚠️ Batch {batch_num} ล้มเหลว: {e}")
        # รอนานขึ้นถ้าเกิดข้อผิดพลาด
        print("⏳ รอ 10 วินาทีแล้วลองใหม่...")
        time.sleep(10)

conn.close()
print("\n✅ การจัดรูปแบบสีเสร็จสิ้นแล้ว!")
print("🎨 แต่ละ Order ID จะมีสีที่แตกต่างกัน:")
print("   - สีอ่อนสำหรับรายการสินค้า")
print("   - สีเข้มสำหรับแถวสรุปยอด")
print("   - ใช้ 6 ชุดสี (ส้ม, เขียว, ฟ้า, ม่วง, ชมพู, เหลือง) หมุนเวียนกัน")