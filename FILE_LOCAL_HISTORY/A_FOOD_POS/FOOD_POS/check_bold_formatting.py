import gspread
from google.oauth2.service_account import Credentials
import json
import time

def check_and_fix_bold_formatting():
    """ตรวจสอบและแก้ไขการจัดรูปแบบตัวหนาใน Google Sheets"""
    
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
        
        # ตรวจหาแถวสรุปยอด (แถวที่มีข้อความ "รวม" หรือ "ยอดรวม")
        summary_rows = []
        bold_issues = []
        
        for i, row in enumerate(all_values, 1):
            # ตรวจสอบว่าเป็นแถวสรุปยอดหรือไม่
            is_summary_row = False
            for cell in row:
                if cell and ('รวม' in str(cell) or 'ยอดรวม' in str(cell) or 'Order' in str(cell)):
                    # ตรวจสอบว่าเป็นแถวสรุปจริงๆ (ไม่ใช่แถวข้อมูลปกติ)
                    if any(keyword in str(cell) for keyword in ['รวม', 'ยอดรวม']) and len([c for c in row if c.strip()]) <= 3:
                        is_summary_row = True
                        summary_rows.append(i)
                        break
            
            # ตรวจสอบการจัดรูปแบบตัวหนาปัจจุบัน
            try:
                # ใช้ batch_get เพื่อตรวจสอบการจัดรูปแบบ
                range_name = f'A{i}:Z{i}'
                result = sheet.values_batch_get([range_name], 
                                               value_render_option='FORMATTED_VALUE',
                                               date_time_render_option='FORMATTED_STRING')
                
                # ตรวจสอบว่ามีการจัดรูปแบบตัวหนาหรือไม่
                # (ในที่นี้เราจะใช้วิธีการตรวจสอบแบบง่าย)
                
            except Exception as e:
                print(f"ไม่สามารถตรวจสอบการจัดรูปแบบแถว {i}: {e}")
        
        print(f"\nพบแถวสรุปยอด {len(summary_rows)} แถว: {summary_rows}")
        
        # ตรวจสอบการจัดรูปแบบโดยใช้ Sheets API
        from googleapiclient.discovery import build
        
        service = build('sheets', 'v4', credentials=creds)
        
        # อ่านการจัดรูปแบบทั้งหมด
        range_name = f'A1:Z{len(all_values)}'
        result = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            ranges=[range_name],
            includeGridData=True
        ).execute()
        
        sheets_data = result.get('sheets', [])
        if not sheets_data:
            print("ไม่พบข้อมูลชีต")
            return
        
        grid_data = sheets_data[0].get('data', [])
        if not grid_data:
            print("ไม่พบข้อมูลตาราง")
            return
        
        row_data = grid_data[0].get('rowData', [])
        
        # ตรวจสอบแถวที่มีตัวหนาผิด
        wrong_bold_rows = []
        correct_bold_rows = []
        
        for i, row in enumerate(row_data, 1):
            values = row.get('values', [])
            has_bold = False
            
            for cell in values:
                text_format = cell.get('effectiveFormat', {}).get('textFormat', {})
                if text_format.get('bold', False):
                    has_bold = True
                    break
            
            if has_bold:
                if i in summary_rows:
                    correct_bold_rows.append(i)
                else:
                    wrong_bold_rows.append(i)
        
        print(f"\n=== ผลการตรวจสอบ ===")
        print(f"แถวที่มีตัวหนาถูกต้อง (แถวสรุปยอด): {len(correct_bold_rows)} แถว")
        print(f"แถวที่มีตัวหนาผิด (ไม่ใช่แถวสรุปยอด): {len(wrong_bold_rows)} แถว")
        
        if wrong_bold_rows:
            print(f"\nแถวที่มีตัวหนาผิด: {wrong_bold_rows[:20]}{'...' if len(wrong_bold_rows) > 20 else ''}")
            
            # แสดงตัวอย่างข้อมูลในแถวที่ผิด
            print("\nตัวอย่างข้อมูลในแถวที่มีตัวหนาผิด:")
            for row_num in wrong_bold_rows[:5]:
                if row_num <= len(all_values):
                    row_data_sample = all_values[row_num-1]
                    print(f"แถว {row_num}: {row_data_sample[:5]}")
        
        # ถามผู้ใช้ว่าต้องการแก้ไขหรือไม่
        if wrong_bold_rows:
            print(f"\nพบแถวที่มีตัวหนาผิด {len(wrong_bold_rows)} แถว")
            fix_choice = input("ต้องการแก้ไขการจัดรูปแบบตัวหนาหรือไม่? (y/n): ")
            
            if fix_choice.lower() == 'y':
                print("กำลังแก้ไขการจัดรูปแบบ...")
                
                # สร้าง batch requests เพื่อลบตัวหนาจากแถวที่ผิด
                requests = []
                
                for row_num in wrong_bold_rows:
                    # ลบตัวหนาจากแถวทั้งแถว
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
                                        'bold': False
                                    }
                                }
                            },
                            'fields': 'userEnteredFormat.textFormat.bold'
                        }
                    })
                
                # ทำการแก้ไขเป็นชุดๆ เพื่อหลีกเลี่ยงข้อจำกัดของ API
                batch_size = 100
                for i in range(0, len(requests), batch_size):
                    batch_requests = requests[i:i + batch_size]
                    
                    try:
                        service.spreadsheets().batchUpdate(
                            spreadsheetId=spreadsheet_id,
                            body={'requests': batch_requests}
                        ).execute()
                        
                        print(f"แก้ไขแล้ว {min(i + batch_size, len(requests))}/{len(requests)} แถว")
                        time.sleep(1)  # หน่วงเวลาเพื่อหลีกเลี่ยงการเรียก API เร็วเกินไป
                        
                    except Exception as e:
                        print(f"เกิดข้อผิดพลาดในการแก้ไข batch {i//batch_size + 1}: {e}")
                
                print("\n=== การแก้ไขเสร็จสิ้น ===")
                print(f"ลบตัวหนาจากแถวที่ผิด {len(wrong_bold_rows)} แถวแล้ว")
                print(f"ตอนนี้มีเฉพาะแถวสรุปยอดเท่านั้นที่เป็นตัวหนา")
                
        else:
            print("\n✅ การจัดรูปแบบตัวหนาถูกต้องแล้ว!")
            print("มีเฉพาะแถวสรุปยอดเท่านั้นที่เป็นตัวหนา")
        
        # แสดง URL ของ Google Sheets
        sheets_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
        print(f"\nGoogle Sheets URL: {sheets_url}")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== ตรวจสอบการจัดรูปแบบตัวหนาใน Google Sheets ===")
    print("สคริปต์นี้จะตรวจสอบและแก้ไขการใส่ตัวหนาให้มีเฉพาะแถวสรุปยอดเท่านั้น")
    print()
    
    check_and_fix_bold_formatting()
    
    print("\nการตรวจสอบเสร็จสิ้น")