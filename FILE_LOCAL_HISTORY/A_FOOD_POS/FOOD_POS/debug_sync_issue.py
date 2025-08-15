import sqlite3
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import json

def connect_to_database():
    """เชื่อมต่อกับฐานข้อมูล SQLite"""
    return sqlite3.connect('pos_database.db')

def get_google_sheets_client():
    """เชื่อมต่อกับ Google Sheets"""
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
    client = gspread.authorize(creds)
    return client

def check_database_data():
    """ตรวจสอบข้อมูลในฐานข้อมูล"""
    conn = connect_to_database()
    cursor = conn.cursor()
    
    print("=== ตรวจสอบข้อมูลในฐานข้อมูล ===")
    
    # ตรวจสอบข้อมูลวันที่ 2025-08-12
    cursor.execute("""
        SELECT DATE(created_at) as order_date, 
               COUNT(*) as order_count,
               SUM(total_amount) as total_sales,
               status
        FROM orders 
        WHERE DATE(created_at) = '2025-08-12'
        GROUP BY DATE(created_at), status
        ORDER BY status
    """)
    
    results = cursor.fetchall()
    print("\nข้อมูลวันที่ 2025-08-12 ตามสถานะ:")
    for row in results:
        print(f"วันที่: {row[0]}, จำนวนออเดอร์: {row[1]}, ยอดรวม: {row[2]:.2f}, สถานะ: {row[3]}")
    
    # ตรวจสอบข้อมูลรวมทั้งหมด (ยกเว้น rejected)
    cursor.execute("""
        SELECT DATE(created_at) as order_date, 
               COUNT(*) as order_count,
               SUM(total_amount) as total_sales
        FROM orders 
        WHERE DATE(created_at) = '2025-08-12' AND status != 'rejected'
        GROUP BY DATE(created_at)
    """)
    
    result = cursor.fetchone()
    if result:
        print(f"\nข้อมูลรวม (ยกเว้น rejected): วันที่ {result[0]}, จำนวนออเดอร์: {result[1]}, ยอดรวม: {result[2]:.2f}")
    else:
        print("\nไม่พบข้อมูลรวมสำหรับวันที่ 2025-08-12")
    
    # ตรวจสอบข้อมูลล่าสุด 5 วัน
    cursor.execute("""
        SELECT DATE(created_at) as order_date, 
               COUNT(*) as order_count,
               SUM(total_amount) as total_sales
        FROM orders 
        WHERE status != 'rejected'
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at) DESC
        LIMIT 5
    """)
    
    results = cursor.fetchall()
    print("\nข้อมูลล่าสุด 5 วัน (ยกเว้น rejected):")
    for row in results:
        print(f"วันที่: {row[0]}, จำนวนออเดอร์: {row[1]}, ยอดรวม: {row[2]:.2f}")
    
    conn.close()
    return results

def check_google_sheets_data():
    """ตรวจสอบข้อมูลใน Google Sheets"""
    try:
        client = get_google_sheets_client()
        
        # อ่านไฟล์ config
        with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        spreadsheet_id = config['spreadsheet_id']
        sheet = client.open_by_key(spreadsheet_id)
        
        print("\n=== ตรวจสอบข้อมูลใน Google Sheets ===")
        
        # ตรวจสอบชีท Daily_Summary
        try:
            daily_sheet = sheet.worksheet('Daily_Summary')
            daily_data = daily_sheet.get_all_values()
            
            print("\nข้อมูลในชีท Daily_Summary:")
            print(f"จำนวนแถว: {len(daily_data)}")
            
            if len(daily_data) > 1:
                print("\nข้อมูล 5 แถวล่าสุด:")
                for i, row in enumerate(daily_data[-5:], 1):
                    print(f"แถวที่ {len(daily_data)-5+i}: {row}")
                
                # ค้นหาข้อมูลวันที่ 2025-08-12
                found_2025_08_12 = False
                for i, row in enumerate(daily_data):
                    if len(row) > 0 and '2025-08-12' in str(row[0]):
                        print(f"\nพบข้อมูลวันที่ 2025-08-12 ในแถวที่ {i+1}: {row}")
                        found_2025_08_12 = True
                        break
                
                if not found_2025_08_12:
                    print("\nไม่พบข้อมูลวันที่ 2025-08-12 ในชีท Daily_Summary")
            
        except Exception as e:
            print(f"ข้อผิดพลาดในการอ่านชีท Daily_Summary: {e}")
        
        # ตรวจสอบชีท Monthly_Summary
        try:
            monthly_sheet = sheet.worksheet('Monthly_Summary')
            monthly_data = monthly_sheet.get_all_values()
            
            print("\nข้อมูลในชีท Monthly_Summary:")
            print(f"จำนวนแถว: {len(monthly_data)}")
            
            if len(monthly_data) > 1:
                print("\nข้อมูลทั้งหมด:")
                for i, row in enumerate(monthly_data, 1):
                    print(f"แถวที่ {i}: {row}")
            
        except Exception as e:
            print(f"ข้อผิดพลาดในการอ่านชีท Monthly_Summary: {e}")
            
    except Exception as e:
        print(f"ข้อผิดพลาดในการเชื่อมต่อ Google Sheets: {e}")

def manual_sync_data():
    """ซิงค์ข้อมูลด้วยตนเอง"""
    print("\n=== เริ่มการซิงค์ข้อมูลด้วยตนเอง ===")
    
    try:
        # เชื่อมต่อฐานข้อมูล
        conn = connect_to_database()
        cursor = conn.cursor()
        
        # ดึงข้อมูลยอดขายรายวัน
        cursor.execute("""
            SELECT DATE(created_at) as order_date, 
                   COUNT(*) as order_count,
                   SUM(total_amount) as total_sales
            FROM orders 
            WHERE status != 'rejected'
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at) DESC
            LIMIT 15
        """)
        
        daily_data = cursor.fetchall()
        print(f"\nดึงข้อมูลยอดขายรายวัน: {len(daily_data)} รายการ")
        
        # เชื่อมต่อ Google Sheets
        client = get_google_sheets_client()
        
        with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        spreadsheet_id = config['spreadsheet_id']
        sheet = client.open_by_key(spreadsheet_id)
        
        # อัปเดตชีท Daily_Summary
        daily_sheet = sheet.worksheet('Daily_Summary')
        
        # ล้างข้อมูลเก่า
        daily_sheet.clear()
        
        # เพิ่มหัวตาราง
        headers = ['วันที่', 'จำนวนออเดอร์', 'ยอดขายรวม (บาท)']
        daily_sheet.append_row(headers)
        
        # เพิ่มข้อมูลใหม่
        for row in daily_data:
            date_str = datetime.strptime(row[0], '%Y-%m-%d').strftime('%d/%m/%Y')
            formatted_row = [date_str, row[1], f"{row[2]:.2f}"]
            daily_sheet.append_row(formatted_row)
            print(f"เพิ่มข้อมูล: {formatted_row}")
        
        print(f"\nอัปเดตชีท Daily_Summary สำเร็จ: {len(daily_data)} รายการ")
        
        conn.close()
        
    except Exception as e:
        print(f"ข้อผิดพลาดในการซิงค์ข้อมูล: {e}")

if __name__ == "__main__":
    print("=== เริ่มการตรวจสอบและแก้ไขปัญหาการซิงค์ข้อมูล ===")
    
    # ตรวจสอบข้อมูลในฐานข้อมูล
    db_data = check_database_data()
    
    # ตรวจสอบข้อมูลใน Google Sheets
    check_google_sheets_data()
    
    # ถามผู้ใช้ว่าต้องการซิงค์ข้อมูลหรือไม่
    response = input("\nต้องการซิงค์ข้อมูลด้วยตนเองหรือไม่? (y/n): ")
    if response.lower() == 'y':
        manual_sync_data()
        print("\nการซิงค์ข้อมูลเสร็จสิ้น กรุณาตรวจสอบ Google Sheets อีกครั้ง")
    else:
        print("\nยกเลิกการซิงค์ข้อมูล")