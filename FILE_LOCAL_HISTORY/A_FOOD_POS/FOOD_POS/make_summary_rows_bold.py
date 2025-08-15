import json
import gspread
from google.oauth2.service_account import Credentials
from collections import defaultdict

# โหลดการตั้งค่า Google Sheets
with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# ตั้งค่า Google Sheets API
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPE)
client = gspread.authorize(creds)

# เปิด Google Sheets
sheet = client.open_by_key(config['spreadsheet_id'])
worksheet = sheet.worksheet('Orders')

print("เชื่อมต่อกับ Google Sheets สำเร็จ")
print(f"กำลังจัดรูปแบบตัวหนาสำหรับแถวสรุปยอด...")

# ดึงข้อมูลทั้งหมด
all_data = worksheet.get_all_values()
if not all_data:
    print("ไม่พบข้อมูลใน Google Sheets")
    exit()

# หาแถวสรุปยอด (แถวที่มี "สรุป Order" และ "รวม" และ "รายการ")
summary_rows = []
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

# จัดรูปแบบตัวหนาสำหรับแถวสรุปยอดแบบ batch
if summary_rows:
    # ใช้ Google Sheets API เพื่อ batch formatting
    from googleapiclient.discovery import build
    
    service = build('sheets', 'v4', credentials=creds)
    
    # สร้าง batch requests
    requests = []
    
    for row_num in summary_rows:
        # หาคอลัมน์สุดท้ายที่มีข้อมูล
        row_data = all_data[row_num - 1]
        last_col = len(row_data)
        
        # หาคอลัมน์สุดท้ายที่มีข้อมูลจริง (ไม่ใช่ค่าว่าง)
        while last_col > 0 and (not row_data[last_col - 1] or row_data[last_col - 1].strip() == ''):
            last_col -= 1
        
        if last_col == 0:
            continue
        
        # เพิ่ม request สำหรับจัดรูปแบบตัวหนา
        requests.append({
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': row_num - 1,
                    'endRowIndex': row_num,
                    'startColumnIndex': 0,
                    'endColumnIndex': last_col
                },
                'cell': {
                    'userEnteredFormat': {
                        'textFormat': {
                            'bold': True
                        }
                    }
                },
                'fields': 'userEnteredFormat.textFormat.bold'
            }
        })
        
        print(f"เตรียมจัดรูปแบบตัวหนาสำหรับแถว {row_num} (คอลัมน์ A-{chr(64+last_col)})")
    
    # ส่ง batch request
    if requests:
        body = {'requests': requests}
        service.spreadsheets().batchUpdate(
            spreadsheetId=config['spreadsheet_id'],
            body=body
        ).execute()
        
        print(f"จัดรูปแบบตัวหนาสำเร็จสำหรับ {len(requests)} แถว")

print(f"\nจัดรูปแบบตัวหนาสำหรับแถวสรุปยอดเสร็จสมบูรณ์!")
print(f"จัดรูปแบบทั้งหมด {len(summary_rows)} แถว")
print(f"\nGoogle Sheets URL: https://docs.google.com/spreadsheets/d/{config['spreadsheet_id']}")