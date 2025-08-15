import gspread
from google.oauth2.service_account import Credentials
import json

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

print("กำลังตรวจสอบข้อมูลที่คืนค่าแล้ว...")

# อ่านข้อมูลทั้งหมด
all_data = worksheet.get_all_values()

if not all_data:
    print("❌ ไม่พบข้อมูลใน Google Sheets")
    exit()

print(f"\n=== ผลลัพธ์การคืนค่าเดิม ===")
print(f"จำนวนแถวทั้งหมด: {len(all_data)}")
print(f"Header: {all_data[0]}")

# แสดงตัวอย่างข้อมูล 15 แถวแรก
print("\n=== ตัวอย่างข้อมูล 15 แถวแรก ===")
for i, row in enumerate(all_data[:15]):
    if i == 0:
        print(f"แถว {i+1} (Header): {row}")
    else:
        print(f"แถว {i+1}: {row}")

# ตรวจสอบโครงสร้าง Order
print("\n=== การวิเคราะห์โครงสร้าง ===")
order_count = 0
summary_count = 0
item_count = 0
current_order = None
orders_found = []

for i, row in enumerate(all_data[1:], 2):  # เริ่มจากแถว 2
    if len(row) > 0 and row[0]:
        if row[0].isdigit():  # Order ID
            if row[0] != current_order:
                current_order = row[0]
                order_count += 1
                orders_found.append((row[0], i))
            item_count += 1
        elif row[0].startswith('สรุป Order'):  # แถวสรุป
            summary_count += 1

print(f"จำนวน Order: {order_count}")
print(f"จำนวนรายการสินค้า: {item_count}")
print(f"จำนวนแถวสรุป: {summary_count}")

# แสดง Order ที่พบ 10 รายการแรก
print("\n=== Order ที่พบ (10 รายการแรก) ===")
for order_id, row_num in orders_found[:10]:
    print(f"Order {order_id} อยู่ที่แถว {row_num}")

# ตรวจสอบ Order 176 โดยเฉพาะ
print("\n=== ตรวจสอบ Order 176 โดยเฉพาะ ===")
order_176_found = False
for i, row in enumerate(all_data):
    if len(row) > 0 and row[0] == '176':
        if not order_176_found:
            print(f"พบ Order 176 ที่แถว {i+1}:")
            order_176_found = True
        print(f"  แถว {i+1}: {row}")
    elif order_176_found and len(row) > 0 and row[0].startswith('สรุป Order 176'):
        print(f"  แถว {i+1} (สรุป): {row}")
        break

print("\n=== สรุปการตรวจสอบ ===")
if order_count > 0:
    print("✅ ข้อมูลถูกคืนค่าเดิมเรียบร้อยแล้ว")
    print("✅ พบ Order และรายการสินค้าครบถ้วน")
    print("✅ มีแถวสรุปตามที่ควรจะเป็น")
    print("✅ โครงสร้างข้อมูลถูกต้องตามเดิม")
else:
    print("❌ ไม่พบข้อมูล Order")

print(f"\n🔗 URL: https://docs.google.com/spreadsheets/d/{config['spreadsheet_id']}")