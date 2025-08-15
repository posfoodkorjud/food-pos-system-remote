import gspread
from google.oauth2.service_account import Credentials
import json
import time
import os
from googleapiclient.discovery import build

def complete_reset_and_restore():
    """ลบข้อมูลทั้งหมดใน Google Sheets และคืนค่าจากไฟล์สำรอง"""
    
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
        
        print("เชื่อมต่อกับ Google Sheets สำเร็จ")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
        return
    
    try:
        print("\n=== ขั้นตอนที่ 1: ลบข้อมูลทั้งหมดใน Google Sheets ===")
        
        # ดึงรายชื่อ worksheets ทั้งหมด
        worksheets = sheet.worksheets()
        print(f"พบ worksheets ทั้งหมด {len(worksheets)} ชีต")
        
        for ws in worksheets:
            print(f"ชีต: {ws.title}")
        
        # ลบ worksheets ทั้งหมดยกเว้นชีตแรก
        if len(worksheets) > 1:
            for ws in worksheets[1:]:
                try:
                    sheet.del_worksheet(ws)
                    print(f"ลบชีต '{ws.title}' สำเร็จ")
                    time.sleep(1)
                except Exception as e:
                    print(f"เกิดข้อผิดพลาดในการลบชีต '{ws.title}': {e}")
        
        # ล้างข้อมูลในชีตแรกและเปลี่ยนชื่อเป็น 'Orders'
        main_worksheet = sheet.get_worksheet(0)
        
        # เปลี่ยนชื่อชีตเป็น 'Orders'
        try:
            main_worksheet.update_title('Orders')
            print("เปลี่ยนชื่อชีตหลักเป็น 'Orders' สำเร็จ")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการเปลี่ยนชื่อชีต: {e}")
        
        # ล้างข้อมูลทั้งหมดในชีต Orders
        try:
            # ล้างข้อมูลในช่วง A1:Z1000 (ครอบคลุมพื้นที่ใหญ่)
            main_worksheet.batch_clear(['A1:Z1000'])
            print("ล้างข้อมูลทั้งหมดในชีต Orders สำเร็จ")
            
            # ล้างการจัดรูปแบบทั้งหมด
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
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
                            'horizontalAlignment': 'LEFT',
                            'verticalAlignment': 'BOTTOM',
                            'backgroundColor': {'red': 1, 'green': 1, 'blue': 1}
                        }
                    },
                    'fields': 'userEnteredFormat'
                }
            }]
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            print("ล้างการจัดรูปแบบทั้งหมดสำเร็จ")
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการล้างข้อมูล: {e}")
        
        print("\n✅ ลบข้อมูลทั้งหมดเสร็จสิ้น - Google Sheets กลับเป็นสถานะเริ่มต้น")
        
        print("\n=== ขั้นตอนที่ 2: ค้นหาไฟล์สำรองล่าสุด ===")
        
        # ค้นหาไฟล์สำรองในโฟลเดอร์ sheets_backups
        backup_dir = 'sheets_backups'
        
        if not os.path.exists(backup_dir):
            print(f"ไม่พบโฟลเดอร์ {backup_dir}")
            return
        
        # ค้นหาไฟล์ sheets_data_*.json ในโฟลเดอร์สำรอง
        backup_files = []
        for file in os.listdir(backup_dir):
            if file.startswith('sheets_data_') and file.endswith('.json'):
                file_path = os.path.join(backup_dir, file)
                backup_files.append((file, os.path.getmtime(file_path)))
        
        if not backup_files:
            print(f"ไม่พบไฟล์สำรอง sheets_data_*.json ในโฟลเดอร์ {backup_dir}")
            return
        
        # เรียงลำดับตามวันที่แก้ไขล่าสุด
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        print(f"พบไฟล์สำรองทั้งหมด {len(backup_files)} ไฟล์:")
        for i, (filename, timestamp) in enumerate(backup_files, 1):
            import datetime
            date_str = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {i}. {filename} (แก้ไขล่าสุด: {date_str})")
        
        # ใช้ไฟล์สำรองล่าสุด
        latest_backup = backup_files[0][0]
        backup_path = os.path.join(backup_dir, latest_backup)
        
        print(f"\nเลือกใช้ไฟล์สำรองล่าสุด: {latest_backup}")
        
        print("\n=== ขั้นตอนที่ 3: คืนค่าข้อมูลจากไฟล์สำรอง ===")
        
        # อ่านข้อมูลจากไฟล์สำรอง
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_json = json.load(f)
            
            # ดึงข้อมูลจาก key 'data'
            backup_data = backup_json.get('data', [])
            
            print(f"อ่านไฟล์สำรองสำเร็จ: {len(backup_data)} แถว")
            
            if not backup_data:
                print("ไฟล์สำรองไม่มีข้อมูล")
                return
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการอ่านไฟล์สำรอง: {e}")
            return
        
        # คืนค่าข้อมูลไปยัง Google Sheets
        try:
            # เตรียมข้อมูลสำหรับการอัปเดต
            num_rows = len(backup_data)
            num_cols = max(len(row) for row in backup_data) if backup_data else 0
            
            # แปลงหมายเลขคอลัมน์เป็นตัวอักษร
            def num_to_col_letters(num):
                result = ""
                while num > 0:
                    num -= 1
                    result = chr(num % 26 + ord('A')) + result
                    num //= 26
                return result
            
            end_col = num_to_col_letters(num_cols)
            range_name = f'A1:{end_col}{num_rows}'
            
            print(f"กำลังคืนค่าข้อมูล {num_rows} แถว {num_cols} คอลัมน์ (ช่วง: {range_name})")
            
            # อัปเดตข้อมูลทีละชุด
            batch_size = 100
            for i in range(0, num_rows, batch_size):
                end_idx = min(i + batch_size, num_rows)
                batch_data = backup_data[i:end_idx]
                
                start_row = i + 1
                end_row = end_idx
                batch_range = f'A{start_row}:{end_col}{end_row}'
                
                # แปลงข้อมูลให้เป็น string ทั้งหมด
                clean_batch_data = []
                for row in batch_data:
                    clean_row = [str(cell) if cell is not None else '' for cell in row]
                    clean_batch_data.append(clean_row)
                
                main_worksheet.update(batch_range, clean_batch_data, value_input_option='RAW')
                
                print(f"คืนค่าข้อมูลแล้ว {end_idx}/{num_rows} แถว")
                time.sleep(1)
            
            print("\n✅ คืนค่าข้อมูลทั้งหมดสำเร็จ")
            
            # ตรวจสอบข้อมูลที่คืนค่า
            restored_data = main_worksheet.get_all_values()
            print(f"\nการตรวจสอบ: พบข้อมูลทั้งหมด {len(restored_data)} แถว")
            
            # แสดงตัวอย่างข้อมูล 5 แถวแรก
            if restored_data:
                print("\nตัวอย่างข้อมูล 5 แถวแรก:")
                for i, row in enumerate(restored_data[:5], 1):
                    row_preview = [str(cell)[:20] + '...' if len(str(cell)) > 20 else str(cell) for cell in row[:5]]
                    print(f"  แถว {i}: {row_preview}")
            
            # นับจำนวน Order
            order_count = 0
            for row in restored_data:
                if any('สรุป Order' in str(cell) and 'รวม' in str(cell) for cell in row):
                    order_count += 1
            
            print(f"\nพบ Order ทั้งหมด: {order_count} รายการ")
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการคืนค่าข้อมูล: {e}")
            import traceback
            traceback.print_exc()
            return
        
        print("\n=== ขั้นตอนที่ 4: ปรับปรุงการจัดรูปแบบ ===")
        
        # อ่านข้อมูลที่คืนค่าแล้วเพื่อจัดรูปแบบ
        try:
            all_values = main_worksheet.get_all_values()
            
            # จำแนกประเภทแถว
            header_rows = []
            summary_rows = []
            data_rows = []
            
            for i, row in enumerate(all_values, 1):
                if i == 1 and any('Order ID' in str(cell) for cell in row):
                    header_rows.append(i)
                elif any('สรุป Order' in str(cell) and 'รวม' in str(cell) for cell in row):
                    summary_rows.append(i)
                elif any(str(cell).strip() for cell in row):  # แถวที่มีข้อมูล
                    data_rows.append(i)
            
            print(f"แถว Header: {len(header_rows)} แถว")
            print(f"แถวสรุปยอด: {len(summary_rows)} แถว")
            print(f"แถวข้อมูล: {len(data_rows)} แถว")
            
            # สร้าง batch requests สำหรับการจัดรูปแบบ
            requests = []
            
            # จัดรูปแบบ Header
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
            
            # จัดรูปแบบแถวสรุปยอด
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
            
            # จัดรูปแบบแถวข้อมูล
            if data_rows:
                # จัดกลุ่มแถวข้อมูลเป็นช่วงๆ
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
            
            # ใส่สีแบบสลับแถวสำหรับแถวข้อมูล
            for i, row_num in enumerate(data_rows):
                if i % 2 == 1:  # แถวคี่
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
                                    'backgroundColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}
                                }
                            },
                            'fields': 'userEnteredFormat.backgroundColor'
                        }
                    })
            
            # ทำการจัดรูปแบบเป็นชุดๆ
            if requests:
                print("กำลังจัดรูปแบบ...")
                
                batch_size = 50
                for i in range(0, len(requests), batch_size):
                    batch_requests = requests[i:i + batch_size]
                    
                    try:
                        service.spreadsheets().batchUpdate(
                            spreadsheetId=spreadsheet_id,
                            body={'requests': batch_requests}
                        ).execute()
                        
                        print(f"จัดรูปแบบแล้ว {min(i + batch_size, len(requests))}/{len(requests)} รายการ")
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f"เกิดข้อผิดพลาดในการจัดรูปแบบ batch {i//batch_size + 1}: {e}")
                
                print("\n✅ จัดรูปแบบเสร็จสิ้น")
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการจัดรูปแบบ: {e}")
        
        print("\n=== สรุปผลการดำเนินการ ===")
        print("✅ ลบข้อมูลทั้งหมดใน Google Sheets สำเร็จ")
        print(f"✅ คืนค่าข้อมูลจากไฟล์สำรอง '{latest_backup}' สำเร็จ")
        print("✅ จัดรูปแบบใหม่ทั้งหมดสำเร็จ")
        print("✅ Google Sheets กลับเป็นสถานะที่สมบูรณ์แบบ")
        
        # แสดง URL ของ Google Sheets
        sheets_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
        print(f"\nGoogle Sheets URL: {sheets_url}")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดทั่วไป: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== การรีเซ็ตและคืนค่า Google Sheets แบบสมบูรณ์ ===")
    print("สคริปต์นี้จะ:")
    print("1. ลบข้อมูลทั้งหมดใน Google Sheets ให้กลับเป็นสถานะเริ่มต้น")
    print("2. ค้นหาไฟล์สำรองล่าสุดในโฟลเดอร์ sheets_backups")
    print("3. คืนค่าข้อมูลทั้งหมดจากไฟล์สำรอง")
    print("4. จัดรูปแบบใหม่ให้สวยงามและเป็นระเบียบ")
    print()
    
    confirm = input("ยืนยันการดำเนินการ (y/n): ")
    if confirm.lower() == 'y':
        complete_reset_and_restore()
    else:
        print("ยกเลิกการดำเนินการ")
    
    print("\nการดำเนินการเสร็จสิ้น")