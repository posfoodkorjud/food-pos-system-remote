import json
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# โหลดการตั้งค่า Google Sheets
with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# ตั้งค่า Google Sheets API
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPE)
client = gspread.authorize(creds)
service = build('sheets', 'v4', credentials=creds)

# เปิด Google Sheets
sheet = client.open_by_key(config['spreadsheet_id'])
worksheet = sheet.worksheet('Orders')

print("เชื่อมต่อกับ Google Sheets สำเร็จ")
print(f"กำลังหาแถวสรุปยอดและจัดรูปแบบสีเหลืองสำหรับช่องยอดรวม...")

# ดึงข้อมูลทั้งหมด
all_data = worksheet.get_all_values()
if not all_data:
    print("ไม่พบข้อมูลใน Google Sheets")
    exit()

# หาแถวสรุปยอดและคอลัมน์ยอดรวม
summary_rows = []
header_row = all_data[0] if all_data else []

# หาคอลัมน์ยอดรวม (คอลัมน์ F - ราคารวม)
total_col_index = -1
for i, header in enumerate(header_row):
    if 'ราคารวม' in str(header) or 'Total' in str(header):
        total_col_index = i
        break

if total_col_index == -1:
    print("ไม่พบคอลัมน์ยอดรวม")
    exit()

print(f"พบคอลัมน์ยอดรวมที่ตำแหน่ง: {chr(65 + total_col_index)} (index {total_col_index})")

# หาแถวสรุปยอด
for i, row in enumerate(all_data, 1):
    if len(row) > 0:
        row_text = ' '.join(str(cell) for cell in row if str(cell).strip())
        # แถวสรุปยอดจะมีรูปแบบ "สรุป Order XXX" และ "รวม X รายการ"
        if ('สรุป Order' in row_text and 'รวม' in row_text and 'รายการ' in row_text):
            summary_rows.append(i)
            print(f"พบแถวสรุปยอด: แถว {i} - {row_text[:50]}...")

print(f"พบแถวสรุปยอด {len(summary_rows)} แถว")

if not summary_rows:
    print("ไม่พบแถวสรุปยอดใน Google Sheets")
    exit()

# สร้าง batch requests สำหรับจัดรูปแบบสีเหลืองในช่องยอดรวม
requests = []

for row_num in summary_rows:
    # เพิ่ม request สำหรับจัดรูปแบบพื้นหลังสีเหลืองสดในช่องยอดรวม
    requests.append({
        'repeatCell': {
            'range': {
                'sheetId': 0,
                'startRowIndex': row_num - 1,
                'endRowIndex': row_num,
                'startColumnIndex': total_col_index,
                'endColumnIndex': total_col_index + 1
            },
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': {
                        'red': 1.0,    # สีเหลืองสด
                        'green': 1.0,
                        'blue': 0.0
                    },
                    'textFormat': {
                        'bold': True,
                        'foregroundColor': {
                            'red': 0.0,
                            'green': 0.0,
                            'blue': 0.0
                        }
                    }
                }
            },
            'fields': 'userEnteredFormat.backgroundColor,userEnteredFormat.textFormat'
        }
    })
    
    col_letter = chr(65 + total_col_index)
    print(f"เตรียมจัดรูปแบบสีเหลืองสำหรับช่อง {col_letter}{row_num} (ยอดรวมของแถวสรุปยอด)")

# ส่ง batch request
if requests:
    body = {'requests': requests}
    service.spreadsheets().batchUpdate(
        spreadsheetId=config['spreadsheet_id'],
        body=body
    ).execute()
    
    print(f"\nจัดรูปแบบสีเหลืองสำเร็จสำหรับ {len(requests)} ช่องยอดรวม")

print(f"\nจัดรูปแบบสีเหลืองสำหรับช่องยอดรวมในแถวสรุปยอดเสร็จสมบูรณ์!")
print(f"จัดรูปแบบทั้งหมด {len(summary_rows)} แถว")
print(f"\nGoogle Sheets URL: https://docs.google.com/spreadsheets/d/{config['spreadsheet_id']}")