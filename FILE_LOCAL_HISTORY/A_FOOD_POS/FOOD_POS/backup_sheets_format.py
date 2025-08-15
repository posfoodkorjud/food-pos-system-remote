import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json
import os
from datetime import datetime
import pickle

# โหลดการตั้งค่า Google Sheets
with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# ตั้งค่า Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
gc = gspread.authorize(creds)
service = build('sheets', 'v4', credentials=creds)

def create_backup_directory():
    """สร้างโฟลเดอร์สำหรับเก็บไฟล์สำรองข้อมูล"""
    backup_dir = 'sheets_backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"สร้างโฟลเดอร์ {backup_dir} เรียบร้อยแล้ว")
    return backup_dir

def backup_sheet_formatting():
    """สำรองข้อมูลรูปแบบของ Google Sheets"""
    try:
        # เปิด Google Sheets
        spreadsheet = gc.open_by_key(config['spreadsheet_id'])
        
        # สร้างโฟลเดอร์สำรอง
        backup_dir = create_backup_directory()
        
        # สร้างชื่อไฟล์สำรองตามวันที่และเวลา
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"sheets_format_backup_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # ข้อมูลสำรอง
        backup_data = {
            'timestamp': timestamp,
            'spreadsheet_id': config['spreadsheet_id'],
            'spreadsheet_title': spreadsheet.title,
            'worksheets': []
        }
        
        print(f"เริ่มสำรองข้อมูลรูปแบบ Google Sheets: {spreadsheet.title}")
        
        # วนลูปผ่านแต่ละแผ่นงาน
        for worksheet in spreadsheet.worksheets():
            print(f"กำลังสำรองข้อมูลแผ่นงาน: {worksheet.title}")
            
            # ดึงข้อมูลรูปแบบของแผ่นงาน
            sheet_data = service.spreadsheets().get(
                spreadsheetId=config['spreadsheet_id'],
                ranges=[worksheet.title],
                includeGridData=True
            ).execute()
            
            # ดึงข้อมูลทั้งหมดของแผ่นงาน
            all_values = worksheet.get_all_values()
            
            worksheet_backup = {
                'title': worksheet.title,
                'id': worksheet.id,
                'index': worksheet.index,
                'row_count': worksheet.row_count,
                'col_count': worksheet.col_count,
                'values': all_values,
                'sheet_properties': sheet_data['sheets'][0]['properties'],
                'grid_data': sheet_data['sheets'][0].get('data', [])
            }
            
            backup_data['worksheets'].append(worksheet_backup)
        
        # บันทึกข้อมูลสำรองเป็นไฟล์ JSON
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ สำรองข้อมูลเรียบร้อยแล้ว!")
        print(f"📁 ไฟล์สำรอง: {backup_path}")
        print(f"📊 จำนวนแผ่นงานที่สำรอง: {len(backup_data['worksheets'])} แผ่น")
        
        # สร้างไฟล์สำรองแบบย่อ (เฉพาะข้อมูลสำคัญ)
        summary_backup = {
            'timestamp': timestamp,
            'spreadsheet_id': config['spreadsheet_id'],
            'spreadsheet_title': spreadsheet.title,
            'worksheets_summary': []
        }
        
        for ws in backup_data['worksheets']:
            summary_backup['worksheets_summary'].append({
                'title': ws['title'],
                'id': ws['id'],
                'row_count': ws['row_count'],
                'col_count': ws['col_count'],
                'has_data': len(ws['values']) > 0
            })
        
        summary_filename = f"sheets_summary_{timestamp}.json"
        summary_path = os.path.join(backup_dir, summary_filename)
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_backup, f, ensure_ascii=False, indent=2)
        
        print(f"📋 ไฟล์สรุป: {summary_path}")
        
        return backup_path, summary_path
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสำรองข้อมูล: {e}")
        return None, None

def list_backups():
    """แสดงรายการไฟล์สำรองทั้งหมด"""
    backup_dir = 'sheets_backups'
    if not os.path.exists(backup_dir):
        print("ไม่พบโฟลเดอร์สำรองข้อมูล")
        return []
    
    backup_files = []
    for filename in os.listdir(backup_dir):
        if filename.startswith('sheets_format_backup_') and filename.endswith('.json'):
            filepath = os.path.join(backup_dir, filename)
            file_stat = os.stat(filepath)
            backup_files.append({
                'filename': filename,
                'filepath': filepath,
                'size': file_stat.st_size,
                'modified': datetime.fromtimestamp(file_stat.st_mtime)
            })
    
    # เรียงตามวันที่ล่าสุด
    backup_files.sort(key=lambda x: x['modified'], reverse=True)
    
    print("\n📋 รายการไฟล์สำรองข้อมูล:")
    print("-" * 80)
    for i, backup in enumerate(backup_files, 1):
        size_mb = backup['size'] / (1024 * 1024)
        print(f"{i}. {backup['filename']}")
        print(f"   📅 วันที่: {backup['modified'].strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   📦 ขนาด: {size_mb:.2f} MB")
        print()
    
    return backup_files

def restore_from_backup(backup_filepath):
    """กู้คืนข้อมูลจากไฟล์สำรอง"""
    try:
        print(f"กำลังกู้คืนข้อมูลจาก: {backup_filepath}")
        
        # โหลดข้อมูลสำรอง
        with open(backup_filepath, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # เปิด Google Sheets
        spreadsheet = gc.open_by_key(config['spreadsheet_id'])
        
        print(f"กำลังกู้คืนข้อมูลสำหรับ: {backup_data['spreadsheet_title']}")
        print(f"วันที่สำรอง: {backup_data['timestamp']}")
        
        # ลบแผ่นงานที่มีอยู่ (ยกเว้นแผ่นแรก)
        existing_worksheets = spreadsheet.worksheets()
        for ws in existing_worksheets[1:]:  # เก็บแผ่นแรกไว้
            try:
                spreadsheet.del_worksheet(ws)
                print(f"ลบแผ่นงาน: {ws.title}")
            except Exception as e:
                print(f"ไม่สามารถลบแผ่นงาน {ws.title}: {e}")
        
        # กู้คืนแผ่นงานจากข้อมูลสำรอง
        for i, ws_data in enumerate(backup_data['worksheets']):
            try:
                if i == 0:
                    # ใช้แผ่นแรกที่มีอยู่
                    worksheet = existing_worksheets[0]
                    # เปลี่ยนชื่อแผ่นงาน
                    worksheet.update_title(ws_data['title'])
                else:
                    # สร้างแผ่นงานใหม่
                    worksheet = spreadsheet.add_worksheet(
                        title=ws_data['title'],
                        rows=ws_data['row_count'],
                        cols=ws_data['col_count']
                    )
                
                # กู้คืนข้อมูลในแผ่นงาน
                if ws_data['values']:
                    # ล้างข้อมูลเก่า
                    worksheet.clear()
                    
                    # ใส่ข้อมูลใหม่
                    if ws_data['values']:
                        worksheet.update('A1', ws_data['values'])
                
                print(f"✅ กู้คืนแผ่นงาน: {ws_data['title']}")
                
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในการกู้คืนแผ่นงาน {ws_data['title']}: {e}")
        
        print(f"\n🎉 กู้คืนข้อมูลเรียบร้อยแล้ว!")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{config['spreadsheet_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการกู้คืนข้อมูล: {e}")
        return False

def interactive_restore():
    """โหมดกู้คืนข้อมูลแบบโต้ตอบ"""
    backup_files = list_backups()
    
    if not backup_files:
        print("ไม่พบไฟล์สำรองข้อมูล")
        return
    
    print("\n🔄 เลือกไฟล์สำรองที่ต้องการกู้คืน:")
    
    try:
        choice = input("กรุณาใส่หมายเลข (หรือ 'q' เพื่อยกเลิก): ").strip()
        
        if choice.lower() == 'q':
            print("ยกเลิกการกู้คืนข้อมูล")
            return
        
        choice_num = int(choice)
        if 1 <= choice_num <= len(backup_files):
            selected_backup = backup_files[choice_num - 1]
            
            print(f"\n⚠️  คำเตือน: การกู้คืนจะลบข้อมูลปัจจุบันทั้งหมดใน Google Sheets")
            confirm = input("คุณแน่ใจหรือไม่? (y/N): ").strip().lower()
            
            if confirm == 'y':
                restore_from_backup(selected_backup['filepath'])
            else:
                print("ยกเลิกการกู้คืนข้อมูล")
        else:
            print("หมายเลขไม่ถูกต้อง")
            
    except ValueError:
        print("กรุณาใส่หมายเลขที่ถูกต้อง")
    except KeyboardInterrupt:
        print("\nยกเลิกการกู้คืนข้อมูล")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'backup':
            backup_sheet_formatting()
        elif command == 'list':
            list_backups()
        elif command == 'restore':
            interactive_restore()
        else:
            print("คำสั่งไม่ถูกต้อง")
            print("การใช้งาน:")
            print("  python backup_sheets_format.py backup   - สำรองข้อมูล")
            print("  python backup_sheets_format.py list     - แสดงรายการไฟล์สำรอง")
            print("  python backup_sheets_format.py restore  - กู้คืนข้อมูล")
    else:
        # รันโหมดสำรองข้อมูลโดยอัตโนมัติ
        backup_sheet_formatting()