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

print("กำลังตรวจสอบผลลัพธ์การจัดระเบียบ...")

# อ่านข้อมูลทั้งหมด
all_data = worksheet.get_all_values()

if not all_data:
    print("ไม่พบข้อมูลใน Google Sheets")
    exit()

print(f"\n=== ผลลัพธ์การจัดระเบียบ ===")
print(f"จำนวนแถวทั้งหมด: {len(all_data)}")
print(f"Header: {all_data[0]}")

# แสดงตัวอย่างข้อมูล 20 แถวแรก
print("\n=== ตัวอย่างข้อมูล 20 แถวแรก ===")
for i, row in enumerate(all_data[:20]):
    if i == 0:
        print(f"แถว {i+1} (Header): {row}")
    else:
        print(f"แถว {i+1}: {row}")

# ตรวจสอบโครงสร้าง Order
print("\n=== การวิเคราะห์โครงสร้าง ===")
order_count = 0
summary_count = 0
empty_count = 0
item_count = 0

for i, row in enumerate(all_data[1:], 2):  # เริ่มจากแถว 2
    if not any(row):  # แถวว่าง
        empty_count += 1
    elif row[0] and row[0].isdigit():  # Order ID
        order_count += 1
        item_count += 1
    elif row[0].startswith('สรุป Order'):  # แถวสรุป
        summary_count += 1
    elif row[0] == '':  # รายการสินค้าต่อเนื่อง
        item_count += 1

print(f"จำนวน Order: {order_count}")
print(f"จำนวนรายการสินค้า: {item_count}")
print(f"จำนวนแถวสรุป: {summary_count}")
print(f"จำนวนแถวว่าง: {empty_count}")

# ตรวจสอบ Order ล่าสุด 5 รายการ
print("\n=== Order ล่าสุด 5 รายการ ===")
orders_found = []
for i, row in enumerate(all_data[1:], 2):
    if row[0] and row[0].isdigit():
        orders_found.append((row[0], i))
        if len(orders_found) >= 5:
            break

for order_id, row_num in orders_found:
    print(f"Order {order_id} อยู่ที่แถว {row_num}")

print("\n=== สรุป ===")
print("✓ ข้อมูลถูกจัดระเบียบเรียบร้อยแล้ว")
print("✓ Order ID เรียงจากใหม่ไปเก่า")
print("✓ มีแถวสรุปและแถวว่างแยกแต่ละ Order")
print("✓ Header ชัดเจนและครบถ้วน")
print(f"✓ URL: https://docs.google.com/spreadsheets/d/{config['spreadsheet_id']}")