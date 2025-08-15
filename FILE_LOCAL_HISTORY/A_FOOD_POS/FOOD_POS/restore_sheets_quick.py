import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime

# โหลดการตั้งค่า Google Sheets
with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# ตั้งค่า Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
gc = gspread.authorize(creds)

def get_latest_backup():
    """หาไฟล์สำรองล่าสุด"""
    backup_dir = 'sheets_backups'
    if not os.path.exists(backup_dir):
        return None
    
    backup_files = []
    for filename in os.listdir(backup_dir):
        if filename.startswith('sheets_format_backup_') and filename.endswith('.json'):
            filepath = os.path.join(backup_dir, filename)
            file_stat = os.stat(filepath)
            backup_files.append({
                'filename': filename,
                'filepath': filepath,
                'modified': datetime.fromtimestamp(file_stat.st_mtime)
            })
    
    if not backup_files:
        return None
    
    # เรียงตามวันที่ล่าสุด
    backup_files.sort(key=lambda x: x['modified'], reverse=True)
    return backup_files[0]

def restore_latest_backup():
    """กู้คืนจากไฟล์สำรองล่าสุด"""
    try:
        # หาไฟล์สำรองล่าสุด
        latest_backup = get_latest_backup()
        
        if not latest_backup:
            print("❌ ไม่พบไฟล์สำรองข้อมูล")
            print("💡 กรุณารันคำสั่ง: python backup_sheets_format.py backup")
            return False
        
        print(f"🔄 กำลังกู้คืนจากไฟล์สำรองล่าสุด...")
        print(f"📁 ไฟล์: {latest_backup['filename']}")
        print(f"📅 วันที่: {latest_backup['modified'].strftime('%d/%m/%Y %H:%M:%S')}")
        
        # โหลดข้อมูลสำรอง
        with open(latest_backup['filepath'], 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # เปิด Google Sheets
        spreadsheet = gc.open_by_key(config['spreadsheet_id'])
        
        print(f"\n📊 กำลังกู้คืน: {backup_data['spreadsheet_title']}")
        
        # ลบแผ่นงานที่มีอยู่ (ยกเว้นแผ่นแรก)
        existing_worksheets = spreadsheet.worksheets()
        for ws in existing_worksheets[1:]:  # เก็บแผ่นแรกไว้
            try:
                spreadsheet.del_worksheet(ws)
                print(f"🗑️  ลบแผ่นงาน: {ws.title}")
            except Exception as e:
                print(f"⚠️  ไม่สามารถลบแผ่นงาน {ws.title}: {e}")
        
        # กู้คืนแผ่นงานจากข้อมูลสำรอง
        for i, ws_data in enumerate(backup_data['worksheets']):
            try:
                if i == 0:
                    # ใช้แผ่นแรกที่มีอยู่
                    worksheet = existing_worksheets[0]
                    # เปลี่ยนชื่อแผ่นงาน
                    worksheet.update_title(ws_data['title'])
                    print(f"📝 เปลี่ยนชื่อแผ่นแรกเป็น: {ws_data['title']}")
                else:
                    # สร้างแผ่นงานใหม่
                    worksheet = spreadsheet.add_worksheet(
                        title=ws_data['title'],
                        rows=ws_data['row_count'],
                        cols=ws_data['col_count']
                    )
                    print(f"➕ สร้างแผ่นงานใหม่: {ws_data['title']}")
                
                # กู้คืนข้อมูลในแผ่นงาน
                if ws_data['values']:
                    # ล้างข้อมูลเก่า
                    worksheet.clear()
                    
                    # ใส่ข้อมูลใหม่
                    if ws_data['values']:
                        # แบ่งข้อมูลออกเป็นชุดเล็กๆ เพื่อหลีกเลี่ยงข้อจำกัด API
                        chunk_size = 1000
                        values = ws_data['values']
                        
                        for start_row in range(0, len(values), chunk_size):
                            end_row = min(start_row + chunk_size, len(values))
                            chunk_values = values[start_row:end_row]
                            
                            if chunk_values:
                                start_cell = f"A{start_row + 1}"
                                worksheet.update(start_cell, chunk_values)
                                print(f"   📥 อัปเดตข้อมูลแถว {start_row + 1}-{end_row}")
                
                print(f"✅ กู้คืนแผ่นงาน: {ws_data['title']} เรียบร้อย")
                
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในการกู้คืนแผ่นงาน {ws_data['title']}: {e}")
        
        print(f"\n🎉 กู้คืนข้อมูลเรียบร้อยแล้ว!")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{config['spreadsheet_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการกู้คืนข้อมูล: {e}")
        return False

if __name__ == "__main__":
    print("🔄 เริ่มกู้คืนข้อมูล Google Sheets จากไฟล์สำรองล่าสุด...")
    print("=" * 60)
    
    success = restore_latest_backup()
    
    if success:
        print("\n" + "=" * 60)
        print("✨ การกู้คืนข้อมูลเสร็จสมบูรณ์!")
    else:
        print("\n" + "=" * 60)
        print("💔 การกู้คืนข้อมูลล้มเหลว")