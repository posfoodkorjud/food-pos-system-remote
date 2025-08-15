import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json
from datetime import datetime, timedelta
import sqlite3

# โหลดการตั้งค่า Google Sheets
with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# ตั้งค่า Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
gc = gspread.authorize(creds)
service = build('sheets', 'v4', credentials=creds)

# เปิด Google Sheets
spreadsheet = gc.open_by_key(config['spreadsheet_id'])

def create_daily_summary_sheet():
    """สร้างแผ่นชีทสำหรับสรุปยอดขายรายวัน"""
    try:
        # ตรวจสอบว่ามีแผ่นชีท "สรุปยอดขายรายวัน" อยู่แล้วหรือไม่
        try:
            daily_sheet = spreadsheet.worksheet("สรุปยอดขายรายวัน")
            print("แผ่นชีท 'สรุปยอดขายรายวัน' มีอยู่แล้ว")
            return daily_sheet
        except gspread.WorksheetNotFound:
            # สร้างแผ่นชีทใหม่
            daily_sheet = spreadsheet.add_worksheet(title="สรุปยอดขายรายวัน", rows=1000, cols=10)
            print("สร้างแผ่นชีท 'สรุปยอดขายรายวัน' เรียบร้อยแล้ว")
            
            # ตั้งค่าหัวตาราง
            headers = ["วันที่", "จำนวนออเดอร์", "ยอดรวม"]
            daily_sheet.update('A1:C1', [headers])
            
            # จัดรูปแบบหัวตาราง
            requests = []
            
            # ทำให้หัวตารางเป็นตัวหนา
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': daily_sheet.id,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': 3
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {
                                'bold': True
                            },
                            'backgroundColor': {
                                'red': 0.8,
                                'green': 0.8,
                                'blue': 0.8
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            })
            
            # ตั้งค่าความกว้างของคอลัมน์
            requests.append({
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': daily_sheet.id,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 1
                    },
                    'properties': {
                        'pixelSize': 120
                    },
                    'fields': 'pixelSize'
                }
            })
            
            requests.append({
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': daily_sheet.id,
                        'dimension': 'COLUMNS',
                        'startIndex': 1,
                        'endIndex': 2
                    },
                    'properties': {
                        'pixelSize': 150
                    },
                    'fields': 'pixelSize'
                }
            })
            
            requests.append({
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': daily_sheet.id,
                        'dimension': 'COLUMNS',
                        'startIndex': 2,
                        'endIndex': 3
                    },
                    'properties': {
                        'pixelSize': 120
                    },
                    'fields': 'pixelSize'
                }
            })
            
            # ส่งคำขอ batch update
            if requests:
                service.spreadsheets().batchUpdate(
                    spreadsheetId=config['spreadsheet_id'],
                    body={'requests': requests}
                ).execute()
            
            return daily_sheet
            
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการสร้างแผ่นชีท: {e}")
        return None

def create_monthly_summary_sheet():
    """สร้างแผ่นชีทสำหรับสรุปยอดขายรายเดือน"""
    try:
        # ตรวจสอบว่ามีแผ่นชีท "สรุปยอดขายรายเดือน" อยู่แล้วหรือไม่
        try:
            monthly_sheet = spreadsheet.worksheet("สรุปยอดขายรายเดือน")
            print("แผ่นชีท 'สรุปยอดขายรายเดือน' มีอยู่แล้ว")
            return monthly_sheet
        except gspread.WorksheetNotFound:
            # สร้างแผ่นชีทใหม่
            monthly_sheet = spreadsheet.add_worksheet(title="สรุปยอดขายรายเดือน", rows=1000, cols=10)
            print("สร้างแผ่นชีท 'สรุปยอดขายรายเดือน' เรียบร้อยแล้ว")
            
            # ตั้งค่าหัวตาราง
            headers = ["เดือน/ปี", "จำนวนออเดอร์", "ยอดรวม"]
            monthly_sheet.update('A1:C1', [headers])
            
            # จัดรูปแบบหัวตาราง
            requests = []
            
            # ทำให้หัวตารางเป็นตัวหนา
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': monthly_sheet.id,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': 3
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {
                                'bold': True
                            },
                            'backgroundColor': {
                                'red': 0.6,
                                'green': 0.8,
                                'blue': 0.6
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            })
            
            # ตั้งค่าความกว้างของคอลัมน์
            requests.append({
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': monthly_sheet.id,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 1
                    },
                    'properties': {
                        'pixelSize': 120
                    },
                    'fields': 'pixelSize'
                }
            })
            
            requests.append({
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': monthly_sheet.id,
                        'dimension': 'COLUMNS',
                        'startIndex': 1,
                        'endIndex': 2
                    },
                    'properties': {
                        'pixelSize': 150
                    },
                    'fields': 'pixelSize'
                }
            })
            
            requests.append({
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': monthly_sheet.id,
                        'dimension': 'COLUMNS',
                        'startIndex': 2,
                        'endIndex': 3
                    },
                    'properties': {
                        'pixelSize': 120
                    },
                    'fields': 'pixelSize'
                }
            })
            
            # ส่งคำขอ batch update
            if requests:
                service.spreadsheets().batchUpdate(
                    spreadsheetId=config['spreadsheet_id'],
                    body={'requests': requests}
                ).execute()
            
            return monthly_sheet
            
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการสร้างแผ่นชีท: {e}")
        return None

def get_daily_sales_data():
    """ดึงข้อมูลยอดขายรายวันจากฐานข้อมูล"""
    try:
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ดึงข้อมูลยอดขายรายวัน
        query = """
        SELECT 
            DATE(created_at) as sale_date,
            COUNT(*) as order_count,
            SUM(total_amount) as total_sales
        FROM orders 
        WHERE status = 'completed'
        GROUP BY DATE(created_at)
        ORDER BY sale_date DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return results
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
        return []

def get_monthly_sales_data():
    """ดึงข้อมูลยอดขายรายเดือนจากฐานข้อมูล"""
    try:
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ดึงข้อมูลยอดขายรายเดือน
        query = """
        SELECT 
            strftime('%m/%Y', created_at) as sale_month,
            COUNT(*) as order_count,
            SUM(total_amount) as total_sales
        FROM orders 
        WHERE status = 'completed'
        GROUP BY strftime('%Y-%m', created_at)
        ORDER BY strftime('%Y-%m', created_at) DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return results
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
        return []

def update_daily_summary_data(daily_sheet):
    """อัปเดตข้อมูลสรุปยอดขายรายวัน"""
    try:
        # ดึงข้อมูลจากฐานข้อมูล
        daily_data = get_daily_sales_data()
        
        if not daily_data:
            print("ไม่พบข้อมูลยอดขายรายวัน")
            return
        
        # เตรียมข้อมูลสำหรับอัปเดต
        update_data = []
        for row in daily_data:
            sale_date, order_count, total_sales = row
            # แปลงวันที่เป็นรูปแบบที่อ่านง่าย
            date_obj = datetime.strptime(sale_date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d/%m/%Y')
            
            update_data.append([
                formatted_date,
                order_count,
                f"{total_sales:,.2f}"
            ])
        
        # อัปเดตข้อมูลใน Google Sheets
        if update_data:
            # ล้างข้อมูลเก่า (ยกเว้นหัวตาราง)
            daily_sheet.clear()
            
            # เพิ่มหัวตารางกลับ
            headers = ["วันที่", "จำนวนออเดอร์", "ยอดรวม"]
            all_data = [headers] + update_data
            
            # อัปเดตข้อมูลทั้งหมด
            range_name = f"A1:{chr(ord('A') + len(headers) - 1)}{len(all_data)}"
            daily_sheet.update(range_name, all_data)
            
            print(f"อัปเดตข้อมูลสรุปยอดขายรายวัน {len(update_data)} รายการเรียบร้อยแล้ว")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการอัปเดตข้อมูลรายวัน: {e}")

def update_monthly_summary_data(monthly_sheet):
    """อัปเดตข้อมูลสรุปยอดขายรายเดือน"""
    try:
        # ดึงข้อมูลจากฐานข้อมูล
        monthly_data = get_monthly_sales_data()
        
        if not monthly_data:
            print("ไม่พบข้อมูลยอดขายรายเดือน")
            return
        
        # เตรียมข้อมูลสำหรับอัปเดต
        update_data = []
        for row in monthly_data:
            sale_month, order_count, total_sales = row
            
            update_data.append([
                sale_month,
                order_count,
                f"{total_sales:,.2f}"
            ])
        
        # อัปเดตข้อมูลใน Google Sheets
        if update_data:
            # ล้างข้อมูลเก่า (ยกเว้นหัวตาราง)
            monthly_sheet.clear()
            
            # เพิ่มหัวตารางกลับ
            headers = ["เดือน/ปี", "จำนวนออเดอร์", "ยอดรวม"]
            all_data = [headers] + update_data
            
            # อัปเดตข้อมูลทั้งหมด
            range_name = f"A1:{chr(ord('A') + len(headers) - 1)}{len(all_data)}"
            monthly_sheet.update(range_name, all_data)
            
            print(f"อัปเดตข้อมูลสรุปยอดขายรายเดือน {len(update_data)} รายการเรียบร้อยแล้ว")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการอัปเดตข้อมูลรายเดือน: {e}")

if __name__ == "__main__":
    print("เริ่มสร้างแผ่นชีทสรุปยอดขาย...")
    
    # สร้างแผ่นชีทสรุปยอดขายรายวัน
    daily_sheet = create_daily_summary_sheet()
    if daily_sheet:
        update_daily_summary_data(daily_sheet)
    
    # สร้างแผ่นชีทสรุปยอดขายรายเดือน
    monthly_sheet = create_monthly_summary_sheet()
    if monthly_sheet:
        update_monthly_summary_data(monthly_sheet)
    
    print("\nเสร็จสิ้นการสร้างและอัปเดตแผ่นชีทสรุปยอดขาย")
    print(f"URL: https://docs.google.com/spreadsheets/d/{config['spreadsheet_id']}")