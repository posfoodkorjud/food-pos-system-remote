import gspread
from google.oauth2.service_account import Credentials
import json
import time

def apply_correct_bold_formatting():
    """ใส่ตัวหนาให้กับแถวสรุปยอดที่ถูกต้อง"""
    
    # โหลดการตั้งค่า Google Sheets
    try:
        with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        spreadsheet_id = config['spreadsheet_id']
        print(f"กำลังเชื่อมต่อกับ Google Sheets: {spreadsheet_id}")
        
    except FileNotFoundError:
        print("ไม่พบไฟล์ google_sheets_config.json")
        return
    
    # ตั้งค่า Google Sheets API
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        gc = gspread.authorize(creds)
        
        # เปิด Google Sheets
        sheet = gc.open_by_key(spreadsheet_id)
        worksheet = sheet.worksheet('Orders')
        
        print("เชื่อมต่อกับ Google Sheets สำเร็จ")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
        return
    
    try:
        # อ่านข้อมูลทั้งหมด
        all_values = worksheet.get_all_values()
        print(f"อ่านข้อมูลทั้งหมด {len(all_values)} แถว")
        
        # ตรวจหาแถวสรุปยอดที่ถูกต้อง
        summary_rows = []
        header_rows = []
        
        for i, row in enumerate(all_values, 1):
            # ตรวจสอบแถว header
            if i == 1 and any('Order ID' in str(cell) for cell in row):
                header_rows.append(i)
                continue
            
            # ตรวจสอบแถวสรุปยอด
            row_text = ' '.join(str(cell) for cell in row if cell.strip())
            
            # แถวสรุปยอดจะมีรูปแบบ "สรุป Order XXX" และ "รวม X รายการ"
            if ('สรุป Order' in row_text and 'รวม' in row_text and 'รายการ' in row_text):
                summary_rows.append(i)
                print(f"พบแถวสรุปยอด: แถว {i} - {row_text[:50]}...")
        
        print(f"\nพบแถว header: {header_rows}")
        print(f"พบแถวสรุปยอด: {len(summary_rows)} แถว")
        
        if not summary_rows and not header_rows:
            print("ไม่พบแถวที่ต้องใส่ตัวหนา")
            return
        
        # ใช้ Sheets API เพื่อใส่ตัวหนา
        from googleapiclient.discovery import build
        
        service = build('sheets', 'v4', credentials=creds)
        
        # สร้าง batch requests เพื่อใส่ตัวหนา
        requests = []
        
        # ใส่ตัวหนาให้แถว header
        for row_num in header_rows:
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': 0,  # สมมติว่าเป็นชีตแรก
                        'startRowIndex': row_num - 1,
                        'endRowIndex': row_num,
                        'startColumnIndex': 0,
                        'endColumnIndex': 26  # A-Z
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
        
        # ใส่ตัวหนาให้แถวสรุปยอด
        for row_num in summary_rows:
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': 0,  # สมมติว่าเป็นชีตแรก
                        'startRowIndex': row_num - 1,
                        'endRowIndex': row_num,
                        'startColumnIndex': 0,
                        'endColumnIndex': 26  # A-Z
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
        
        if requests:
            print(f"\nกำลังใส่ตัวหนาให้ {len(requests)} แถว...")
            
            # ทำการแก้ไขเป็นชุดๆ เพื่อหลีกเลี่ยงข้อจำกัดของ API
            batch_size = 100
            for i in range(0, len(requests), batch_size):
                batch_requests = requests[i:i + batch_size]
                
                try:
                    service.spreadsheets().batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body={'requests': batch_requests}
                    ).execute()
                    
                    print(f"ใส่ตัวหนาแล้ว {min(i + batch_size, len(requests))}/{len(requests)} แถว")
                    time.sleep(1)  # หน่วงเวลาเพื่อหลีกเลี่ยงการเรียก API เร็วเกินไป
                    
                except Exception as e:
                    print(f"เกิดข้อผิดพลาดในการใส่ตัวหนา batch {i//batch_size + 1}: {e}")
            
            print("\n=== การใส่ตัวหนาเสร็จสิ้น ===")
            print(f"ใส่ตัวหนาให้แถว header: {len(header_rows)} แถว")
            print(f"ใส่ตัวหนาให้แถวสรุปยอด: {len(summary_rows)} แถว")
            print("ตอนนี้มีเฉพาะแถว header และแถวสรุปยอดเท่านั้นที่เป็นตัวหนา")
        
        # แสดง URL ของ Google Sheets
        sheets_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
        print(f"\nGoogle Sheets URL: {sheets_url}")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== ใส่ตัวหนาให้แถวสรุปยอดที่ถูกต้อง ===")
    print("สคริปต์นี้จะใส่ตัวหนาให้กับแถว header และแถวสรุปยอดเท่านั้น")
    print()
    
    apply_correct_bold_formatting()
    
    print("\nการใส่ตัวหนาเสร็จสิ้น")