import gspread
from google.oauth2.service_account import Credentials
import json
import time
from googleapiclient.discovery import build

def comprehensive_formatting_check():
    """ตรวจสอบและปรับปรุงการจัดรูปแบบใน Google Sheets อย่างละเอียด"""
    
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
        service = build('sheets', 'v4', credentials=creds)
        
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
        
        # อ่านการจัดรูปแบบปัจจุบัน
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
        
        print("\n=== การวิเคราะห์การจัดรูปแบบปัจจุบัน ===")
        
        # วิเคราะห์การจัดรูปแบบ
        formatting_issues = {
            'font_size_issues': [],
            'alignment_issues': [],
            'color_issues': [],
            'bold_issues': []
        }
        
        header_rows = []
        summary_rows = []
        data_rows = []
        
        # จำแนกประเภทแถว
        for i, row in enumerate(all_values, 1):
            if i == 1 and any('Order ID' in str(cell) for cell in row):
                header_rows.append(i)
            elif any('สรุป Order' in str(cell) and 'รวม' in str(cell) for cell in row):
                summary_rows.append(i)
            else:
                data_rows.append(i)
        
        print(f"แถว Header: {len(header_rows)} แถว")
        print(f"แถวสรุปยอด: {len(summary_rows)} แถว")
        print(f"แถวข้อมูล: {len(data_rows)} แถว")
        
        # ตรวจสอบการจัดรูปแบบแต่ละแถว
        for i, row in enumerate(row_data, 1):
            values = row.get('values', [])
            
            for j, cell in enumerate(values):
                effective_format = cell.get('effectiveFormat', {})
                text_format = effective_format.get('textFormat', {})
                
                # ตรวจสอบขนาดตัวอักษร
                font_size = text_format.get('fontSize', 10)
                
                # ตรวจสอบการจัดตำแหน่ง
                horizontal_align = effective_format.get('horizontalAlignment', 'LEFT')
                vertical_align = effective_format.get('verticalAlignment', 'BOTTOM')
                
                # ตรวจสอบสี
                bg_color = effective_format.get('backgroundColor', {})
                text_color = text_format.get('foregroundColor', {})
                
                # ตรวจสอบตัวหนา
                is_bold = text_format.get('bold', False)
                
                # กำหนดมาตรฐานที่ควรจะเป็น
                expected_font_size = 10
                expected_horizontal_align = 'CENTER'
                expected_vertical_align = 'MIDDLE'
                
                if i in header_rows:
                    expected_font_size = 12
                    expected_bold = True
                elif i in summary_rows:
                    expected_font_size = 11
                    expected_bold = True
                else:
                    expected_bold = False
                
                # ตรวจสอบปัญหา
                if font_size != expected_font_size:
                    formatting_issues['font_size_issues'].append({
                        'row': i, 'col': j+1, 'current': font_size, 'expected': expected_font_size
                    })
                
                if horizontal_align != expected_horizontal_align:
                    formatting_issues['alignment_issues'].append({
                        'row': i, 'col': j+1, 'type': 'horizontal', 
                        'current': horizontal_align, 'expected': expected_horizontal_align
                    })
                
                if vertical_align != expected_vertical_align:
                    formatting_issues['alignment_issues'].append({
                        'row': i, 'col': j+1, 'type': 'vertical',
                        'current': vertical_align, 'expected': expected_vertical_align
                    })
                
                if is_bold != expected_bold:
                    formatting_issues['bold_issues'].append({
                        'row': i, 'col': j+1, 'current': is_bold, 'expected': expected_bold
                    })
        
        # แสดงผลการวิเคราะห์
        print("\n=== ผลการตรวจสอบ ===")
        print(f"ปัญหาขนาดตัวอักษร: {len(formatting_issues['font_size_issues'])} จุด")
        print(f"ปัญหาการจัดตำแหน่ง: {len(formatting_issues['alignment_issues'])} จุด")
        print(f"ปัญหาตัวหนา: {len(formatting_issues['bold_issues'])} จุด")
        
        # แสดงตัวอย่างปัญหา
        if formatting_issues['font_size_issues']:
            print("\nตัวอย่างปัญหาขนาดตัวอักษร (5 รายการแรก):")
            for issue in formatting_issues['font_size_issues'][:5]:
                print(f"  แถว {issue['row']} คอลัมน์ {issue['col']}: ปัจจุบัน {issue['current']} ควรเป็น {issue['expected']}")
        
        if formatting_issues['alignment_issues']:
            print("\nตัวอย่างปัญหาการจัดตำแหน่ง (5 รายการแรก):")
            for issue in formatting_issues['alignment_issues'][:5]:
                print(f"  แถว {issue['row']} คอลัมน์ {issue['col']} ({issue['type']}): ปัจจุบัน {issue['current']} ควรเป็น {issue['expected']}")
        
        # ถามผู้ใช้ว่าต้องการแก้ไขหรือไม่
        total_issues = (len(formatting_issues['font_size_issues']) + 
                       len(formatting_issues['alignment_issues']) + 
                       len(formatting_issues['bold_issues']))
        
        if total_issues > 0:
            print(f"\nพบปัญหาการจัดรูปแบบทั้งหมด {total_issues} จุด")
            fix_choice = input("ต้องการแก้ไขการจัดรูปแบบทั้งหมดหรือไม่? (y/n): ")
            
            if fix_choice.lower() == 'y':
                print("กำลังแก้ไขการจัดรูปแบบ...")
                
                # สร้าง batch requests
                requests = []
                
                # แก้ไขการจัดรูปแบบสำหรับแถว header
                if header_rows:
                    for row_num in header_rows:
                        requests.append({
                            'repeatCell': {
                                'range': {
                                    'sheetId': 0,
                                    'startRowIndex': row_num - 1,
                                    'endRowIndex': row_num,
                                    'startColumnIndex': 0,
                                    'endColumnIndex': 26
                                },
                                'cell': {
                                    'userEnteredFormat': {
                                        'textFormat': {
                                            'bold': True,
                                            'fontSize': 12,
                                            'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}
                                        },
                                        'horizontalAlignment': 'CENTER',
                                        'verticalAlignment': 'MIDDLE',
                                        'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8}
                                    }
                                },
                                'fields': 'userEnteredFormat'
                            }
                        })
                
                # แก้ไขการจัดรูปแบบสำหรับแถวสรุปยอด
                if summary_rows:
                    for row_num in summary_rows:
                        requests.append({
                            'repeatCell': {
                                'range': {
                                    'sheetId': 0,
                                    'startRowIndex': row_num - 1,
                                    'endRowIndex': row_num,
                                    'startColumnIndex': 0,
                                    'endColumnIndex': 26
                                },
                                'cell': {
                                    'userEnteredFormat': {
                                        'textFormat': {
                                            'bold': True,
                                            'fontSize': 11,
                                            'foregroundColor': {'red': 0, 'green': 0, 'blue': 0}
                                        },
                                        'horizontalAlignment': 'CENTER',
                                        'verticalAlignment': 'MIDDLE',
                                        'backgroundColor': {'red': 0.8, 'green': 0.9, 'blue': 0.8}
                                    }
                                },
                                'fields': 'userEnteredFormat'
                            }
                        })
                
                # แก้ไขการจัดรูปแบบสำหรับแถวข้อมูล
                if data_rows:
                    # จัดกลุ่มแถวข้อมูลเป็นช่วงๆ เพื่อประสิทธิภาพ
                    data_ranges = []
                    start_row = None
                    prev_row = None
                    
                    for row_num in sorted(data_rows):
                        if start_row is None:
                            start_row = row_num
                            prev_row = row_num
                        elif row_num == prev_row + 1:
                            prev_row = row_num
                        else:
                            data_ranges.append((start_row, prev_row))
                            start_row = row_num
                            prev_row = row_num
                    
                    if start_row is not None:
                        data_ranges.append((start_row, prev_row))
                    
                    for start_row, end_row in data_ranges:
                        requests.append({
                            'repeatCell': {
                                'range': {
                                    'sheetId': 0,
                                    'startRowIndex': start_row - 1,
                                    'endRowIndex': end_row,
                                    'startColumnIndex': 0,
                                    'endColumnIndex': 26
                                },
                                'cell': {
                                    'userEnteredFormat': {
                                        'textFormat': {
                                            'bold': False,
                                            'fontSize': 10,
                                            'foregroundColor': {'red': 0, 'green': 0, 'blue': 0}
                                        },
                                        'horizontalAlignment': 'CENTER',
                                        'verticalAlignment': 'MIDDLE',
                                        'backgroundColor': {'red': 1, 'green': 1, 'blue': 1}
                                    }
                                },
                                'fields': 'userEnteredFormat'
                            }
                        })
                
                # ทำการแก้ไขเป็นชุดๆ
                if requests:
                    batch_size = 50
                    for i in range(0, len(requests), batch_size):
                        batch_requests = requests[i:i + batch_size]
                        
                        try:
                            service.spreadsheets().batchUpdate(
                                spreadsheetId=spreadsheet_id,
                                body={'requests': batch_requests}
                            ).execute()
                            
                            print(f"แก้ไขแล้ว {min(i + batch_size, len(requests))}/{len(requests)} รายการ")
                            time.sleep(1)
                            
                        except Exception as e:
                            print(f"เกิดข้อผิดพลาดในการแก้ไข batch {i//batch_size + 1}: {e}")
                
                print("\n=== การแก้ไขเสร็จสิ้น ===")
                print("✅ ขนาดตัวอักษร: Header 12pt, สรุปยอด 11pt, ข้อมูล 10pt")
                print("✅ การจัดตำแหน่ง: ทุกเซลล์จัดกึ่งกลางทั้งแนวนอนและแนวตั้ง")
                print("✅ สี: Header สีน้ำเงิน, สรุปยอดสีเขียวอ่อน, ข้อมูลสีขาว")
                print("✅ ตัวหนา: เฉพาะ Header และแถวสรุปยอดเท่านั้น")
                
        else:
            print("\n✅ การจัดรูปแบบถูกต้องแล้วทุกประการ!")
        
        # ตรวจสอบการจัดสีแบบสลับแถว (Zebra Striping)
        print("\n=== การตรวจสอบการจัดสีแบบสลับแถว ===")
        
        # สร้างการจัดสีแบบสลับแถวสำหรับแถวข้อมูล
        zebra_requests = []
        
        # จัดสีแถวข้อมูลแบบสลับ (แถวคู่สีขาว, แถวคี่สีเทาอ่อน)
        for i, row_num in enumerate(data_rows):
            if i % 2 == 1:  # แถวคี่ (index 1, 3, 5, ...)
                zebra_requests.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': row_num - 1,
                            'endRowIndex': row_num,
                            'startColumnIndex': 0,
                            'endColumnIndex': 26
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}
                            }
                        },
                        'fields': 'userEnteredFormat.backgroundColor'
                    }
                })
        
        if zebra_requests:
            apply_zebra = input("ต้องการใส่สีแบบสลับแถวสำหรับแถวข้อมูลหรือไม่? (y/n): ")
            
            if apply_zebra.lower() == 'y':
                print("กำลังใส่สีแบบสลับแถว...")
                
                batch_size = 50
                for i in range(0, len(zebra_requests), batch_size):
                    batch_requests = zebra_requests[i:i + batch_size]
                    
                    try:
                        service.spreadsheets().batchUpdate(
                            spreadsheetId=spreadsheet_id,
                            body={'requests': batch_requests}
                        ).execute()
                        
                        print(f"ใส่สีแล้ว {min(i + batch_size, len(zebra_requests))}/{len(zebra_requests)} แถว")
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f"เกิดข้อผิดพลาดในการใส่สี batch {i//batch_size + 1}: {e}")
                
                print("✅ ใส่สีแบบสลับแถวเสร็จสิ้น")
        
        # แสดง URL ของ Google Sheets
        sheets_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
        print(f"\nGoogle Sheets URL: {sheets_url}")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== ตรวจสอบและปรับปรุงการจัดรูปแบบ Google Sheets อย่างละเอียด ===")
    print("สคริปต์นี้จะตรวจสอบและแก้ไข:")
    print("- ขนาดตัวอักษร (Header 12pt, สรุปยอด 11pt, ข้อมูล 10pt)")
    print("- การจัดตำแหน่ง (กึ่งกลางทั้งแนวนอนและแนวตั้ง)")
    print("- การจัดสี (Header น้ำเงิน, สรุปยอดเขียว, ข้อมูลขาว/เทา)")
    print("- ตัวหนา (เฉพาะ Header และสรุปยอด)")
    print()
    
    comprehensive_formatting_check()
    
    print("\nการตรวจสอบและปรับปรุงเสร็จสิ้น")