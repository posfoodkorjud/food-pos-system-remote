import gspread
from google.oauth2.service_account import Credentials
import json
import time
from googleapiclient.discovery import build

def color_orders_by_group():
    """จัดสีแบบสลับสำหรับ Order ID เดียวกันและแถวสรุปยอดให้เป็นสีเข้มขึ้น"""
    
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
        main_worksheet = sheet.get_worksheet(0)
        
        print("เชื่อมต่อกับ Google Sheets สำเร็จ")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
        return
    
    try:
        print("\n=== กำลังวิเคราะห์ข้อมูลและจัดกลุ่ม Order ID ===")
        
        # อ่านข้อมูลทั้งหมด
        all_values = main_worksheet.get_all_values()
        
        if not all_values:
            print("ไม่พบข้อมูลใน Google Sheets")
            return
        
        # วิเคราะห์ข้อมูลและจัดกลุ่ม Order ID
        order_groups = []
        current_order_id = None
        current_group = []
        
        for i, row in enumerate(all_values, 1):
            # ข้ามแถว Header
            if i == 1 and any('Order ID' in str(cell) for cell in row):
                continue
            
            # ตรวจสอบว่าเป็นแถวที่มีข้อมูล
            if not any(str(cell).strip() for cell in row):
                continue
            
            # ดึง Order ID จากคอลัมน์แรก
            order_id = str(row[0]).strip() if row else ''
            
            # ตรวจสอบว่าเป็นแถวสรุปยอด
            is_summary_row = any('สรุป Order' in str(cell) and 'รวม' in str(cell) for cell in row)
            
            # ถ้าเป็น Order ID ใหม่
            if order_id and order_id != current_order_id and not is_summary_row:
                # บันทึกกลุ่มเก่า
                if current_group:
                    order_groups.append({
                        'order_id': current_order_id,
                        'rows': current_group.copy()
                    })
                
                # เริ่มกลุ่มใหม่
                current_order_id = order_id
                current_group = [i]
            
            # ถ้าเป็นแถวในกลุ่มเดียวกัน
            elif current_order_id:
                current_group.append(i)
        
        # บันทึกกลุ่มสุดท้าย
        if current_group:
            order_groups.append({
                'order_id': current_order_id,
                'rows': current_group.copy()
            })
        
        print(f"พบ Order ทั้งหมด {len(order_groups)} กลุ่ม:")
        for i, group in enumerate(order_groups, 1):
            print(f"  กลุ่ม {i}: Order ID {group['order_id']} ({len(group['rows'])} แถว)")
        
        print("\n=== กำลังจัดสีแบบสลับ ===")
        
        # กำหนดสีสำหรับการสลับ
        colors = [
            {
                'light': {'red': 1.0, 'green': 1.0, 'blue': 0.8},    # สีเหลืองอ่อน
                'dark': {'red': 0.9, 'green': 0.9, 'blue': 0.0}      # สีเหลืองเข้ม
            },
            {
                'light': {'red': 0.8, 'green': 1.0, 'blue': 0.8},    # สีเขียวอ่อน
                'dark': {'red': 0.0, 'green': 0.8, 'blue': 0.0}      # สีเขียวเข้ม
            }
        ]
        
        # สร้าง batch requests สำหรับการจัดสี
        requests = []
        
        for group_index, group in enumerate(order_groups):
            # เลือกสีตามลำดับกลุ่ม (สลับระหว่างเหลืองและเขียว)
            color_set = colors[group_index % 2]
            
            print(f"กลุ่ม {group_index + 1} (Order ID: {group['order_id']}): ใช้สี{'เหลือง' if group_index % 2 == 0 else 'เขียว'}")
            
            # จัดสีสำหรับแต่ละแถวในกลุ่ม
            for row_num in group['rows']:
                # ตรวจสอบว่าเป็นแถวสรุปยอดหรือไม่
                row_data = all_values[row_num - 1] if row_num <= len(all_values) else []
                is_summary_row = any('สรุป Order' in str(cell) and 'รวม' in str(cell) for cell in row_data)
                
                # เลือกสีตามประเภทแถว
                if is_summary_row:
                    background_color = color_set['dark']  # สีเข้มสำหรับแถวสรุปยอด
                    print(f"  แถว {row_num}: สรุปยอด - สี{'เหลืองเข้ม' if group_index % 2 == 0 else 'เขียวเข้ม'}")
                else:
                    background_color = color_set['light']  # สีอ่อนสำหรับแถวข้อมูล
                    print(f"  แถว {row_num}: ข้อมูล - สี{'เหลืองอ่อน' if group_index % 2 == 0 else 'เขียวอ่อน'}")
                
                # สร้าง request สำหรับการจัดสี
                requests.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': row_num - 1,
                            'endRowIndex': row_num,
                            'startColumnIndex': 0,
                            'endColumnIndex': 26  # ครอบคลุม A-Z
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': background_color
                            }
                        },
                        'fields': 'userEnteredFormat.backgroundColor'
                    }
                })
        
        print(f"\nเตรียม requests ทั้งหมด {len(requests)} รายการ")
        
        # ทำการจัดสีเป็นชุดๆ
        if requests:
            print("\n=== กำลังใส่สี ===")
            
            batch_size = 50
            for i in range(0, len(requests), batch_size):
                batch_requests = requests[i:i + batch_size]
                
                try:
                    service.spreadsheets().batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body={'requests': batch_requests}
                    ).execute()
                    
                    print(f"ใส่สีแล้ว {min(i + batch_size, len(requests))}/{len(requests)} รายการ")
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"เกิดข้อผิดพลาดในการใส่สี batch {i//batch_size + 1}: {e}")
            
            print("\n✅ จัดสีแบบสลับเสร็จสิ้น")
        
        print("\n=== สรุปผลการดำเนินการ ===")
        print(f"✅ จัดสีสำหรับ {len(order_groups)} กลุ่ม Order ID")
        print("✅ ใช้สีเหลืองและเขียวสลับกัน")
        print("✅ แถวสรุปยอดใช้สีเข้มกว่าแถวข้อมูล")
        print("✅ การจัดสีแบบสลับเสร็จสมบูรณ์")
        
        # แสดง URL ของ Google Sheets
        sheets_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
        print(f"\nGoogle Sheets URL: {sheets_url}")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดทั่วไป: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== การจัดสีแบบสลับสำหรับ Order ID ===")
    print("สคริปต์นี้จะ:")
    print("1. วิเคราะห์และจัดกลุ่ม Order ID เดียวกัน")
    print("2. ใส่สีเหลืองและเขียวสลับกันสำหรับแต่ละกลุ่ม Order")
    print("3. ใช้สีเข้มสำหรับแถวสรุปยอด และสีอ่อนสำหรับแถวข้อมูล")
    print("4. สีจะสลับไปเรื่อยๆ ตามลำดับ Order ID")
    print()
    
    color_orders_by_group()
    
    print("\nการดำเนินการเสร็จสิ้น")