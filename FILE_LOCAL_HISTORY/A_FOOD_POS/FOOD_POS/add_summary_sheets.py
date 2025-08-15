#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับเพิ่มแผ่นงานสรุปยอดรายวันและรายเดือนใน Google Sheets
โดยจะตรวจสอบและสร้างแผ่นงานที่ขาดหายไป พร้อมจัดรูปแบบให้เข้าใจง่าย
"""

import sys
import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError as e:
    print(f"❌ ไม่สามารถ import Google API libraries: {e}")
    print("กรุณารัน: pip install google-api-python-client google-auth")
    sys.exit(1)

class SummarySheetManager:
    def __init__(self):
        self.service = None
        self.spreadsheet_id = None
        self.credentials_file = 'credentials.json'
        self.db_path = 'pos_database.db'
        
        # โหลดการตั้งค่า
        self.load_config()
        
        # เริ่มต้น Google Sheets service
        self.initialize_service()
    
    def load_config(self):
        """
        โหลดการตั้งค่าจากไฟล์ config
        """
        config_file = 'google_sheets_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.spreadsheet_id = config.get('spreadsheet_id')
                    print(f"📋 โหลด config สำเร็จ: {self.spreadsheet_id}")
            except Exception as e:
                print(f"❌ ข้อผิดพลาดในการโหลด config: {e}")
        else:
            print("❌ ไม่พบไฟล์ google_sheets_config.json")
    
    def initialize_service(self):
        """
        เริ่มต้น Google Sheets service
        """
        try:
            if not os.path.exists(self.credentials_file):
                print(f"❌ ไม่พบไฟล์ {self.credentials_file}")
                return False
            
            # โหลด credentials
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # สร้าง service
            self.service = build('sheets', 'v4', credentials=credentials)
            print("✅ เชื่อมต่อ Google Sheets API สำเร็จ")
            return True
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการเชื่อมต่อ Google Sheets: {e}")
            return False
    
    def write_to_sheet(self, sheet_name: str, values: List[List], range_start: str = 'A1'):
        """
        เขียนข้อมูลลงในแผ่นงาน
        """
        try:
            range_name = f"{sheet_name}!{range_start}"
            values_body = {'values': values}
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=values_body
            ).execute()
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการเขียนข้อมูล: {e}")
    
    def append_to_sheet(self, sheet_name: str, values: List[List]):
        """
        เพิ่มข้อมูลต่อท้ายในแผ่นงาน
        """
        try:
            range_name = f"{sheet_name}!A:Z"
            values_body = {'values': values}
            
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=values_body
            ).execute()
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการเพิ่มข้อมูล: {e}")
    
    def format_sheet_headers(self, sheet_name: str, num_columns: int):
        """
        จัดรูปแบบหัวตาราง
        """
        try:
            # สร้าง range สำหรับหัวตาราง
            end_column = chr(ord('A') + num_columns - 1)
            range_name = f"{sheet_name}!A1:{end_column}1"
            
            # กำหนดรูปแบบ
            format_request = {
                'requests': [{
                    'repeatCell': {
                        'range': {
                            'sheetId': self.get_sheet_id(sheet_name),
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': num_columns
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {
                                    'red': 0.2,
                                    'green': 0.6,
                                    'blue': 0.9
                                },
                                'textFormat': {
                                    'foregroundColor': {
                                        'red': 1.0,
                                        'green': 1.0,
                                        'blue': 1.0
                                    },
                                    'bold': True
                                },
                                'horizontalAlignment': 'CENTER'
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
                    }
                }]
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=format_request
            ).execute()
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการจัดรูปแบบ: {e}")
    
    def get_sheet_id(self, sheet_name: str) -> int:
        """
        ดึง sheet ID จากชื่อแผ่นงาน
        """
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    return sheet['properties']['sheetId']
            
            return 0
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการดึง sheet ID: {e}")
            return 0
        
    def check_existing_sheets(self) -> Dict[str, bool]:
        """
        ตรวจสอบแผ่นงานที่มีอยู่แล้วใน Google Sheets
        """
        try:
            if not self.service or not self.spreadsheet_id:
                return {'Daily_Summary': False, 'Monthly_Summary': False}
            
            # ดึงข้อมูล spreadsheet
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            # ดึงรายชื่อแผ่นงานที่มีอยู่
            existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            
            return {
                'Daily_Summary': 'Daily_Summary' in existing_sheets,
                'Monthly_Summary': 'Monthly_Summary' in existing_sheets
            }
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการตรวจสอบแผ่นงาน: {e}")
            return {'Daily_Summary': False, 'Monthly_Summary': False}
    
    def create_daily_summary_sheet(self) -> bool:
        """
        สร้างแผ่นงานสรุปยอดรายวัน
        """
        try:
            print("🔄 กำลังสร้างแผ่นงาน 'สรุปยอดรายวัน'...")
            
            if not self.service or not self.spreadsheet_id:
                print("❌ ไม่สามารถเชื่อมต่อ Google Sheets")
                return False
            
            # สร้างแผ่นงานใหม่
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': 'Daily_Summary',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 3
                            }
                        }
                    }
                }]
            }
            
            response = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=request_body
            ).execute()
            
            # หัวตาราง
            headers = [
                'วันที่', 'ยอดขาย', 'จำนวนบิล'
            ]
            # เขียนหัวตาราง
            self.write_to_sheet('Daily_Summary', [headers], 'A1')
            # จัดรูปแบบหัวตาราง
            self.format_sheet_headers('Daily_Summary', len(headers))
            
            # เพิ่มข้อมูลจริง
            daily_data = self.get_daily_sales_data()
            if daily_data:
                self.append_to_sheet('Daily_Summary', daily_data)
            
            print("✅ สร้างแผ่นงาน 'สรุปยอดรายวัน' สำเร็จ")
            return True
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการสร้างแผ่นงานสรุปยอดรายวัน: {e}")
            return False
    
    def create_monthly_summary_sheet(self) -> bool:
        """
        สร้างแผ่นงานสรุปยอดรายเดือน
        """
        try:
            print("🔄 กำลังสร้างแผ่นงาน 'สรุปยอดรายเดือน'...")
            
            if not self.service or not self.spreadsheet_id:
                print("❌ ไม่สามารถเชื่อมต่อ Google Sheets")
                return False
            
            # สร้างแผ่นงานใหม่
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': 'Monthly_Summary',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 9
                            }
                        }
                    }
                }]
            }
            
            response = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=request_body
            ).execute()
            
            # หัวตาราง
            headers = [
                'เดือน-ปี', 'ยอดขายรวม (฿)', 'จำนวนออเดอร์', 'ยอดขายเฉลี่ย (฿)',
                'สินค้าขายดี'
            ]
            
            # เขียนหัวตาราง
            self.write_to_sheet('Monthly_Summary', [headers], 'A1')
            
            # จัดรูปแบบหัวตาราง
            self.format_sheet_headers('Monthly_Summary', len(headers))
            
            # เพิ่มข้อมูลจริง
            monthly_data = self.get_monthly_sales_data()
            if monthly_data:
                self.append_to_sheet('Monthly_Summary', monthly_data)
            
            print("✅ สร้างแผ่นงาน 'สรุปยอดรายเดือน' สำเร็จ")
            return True
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการสร้างแผ่นงานสรุปยอดรายเดือน: {e}")
            return False
    
    def get_daily_sales_data(self) -> List[List]:
        """
        ดึงข้อมูลยอดขายรายวันจริงจากฐานข้อมูล
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            daily_data = []
            today = datetime.now()
            
            # ดึงข้อมูล 7 วันย้อนหลัง
            for i in range(7):
                date = today - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                
                # ดึงยอดขายรวมและจำนวนออเดอร์ในวันนั้น
                cursor.execute("""
                    SELECT 
                        COUNT(DISTINCT o.order_id) as order_count,
                        COALESCE(SUM(o.total_amount), 0) as total_sales,
                        COALESCE(AVG(o.total_amount), 0) as avg_sales
                    FROM orders o
                    WHERE DATE(o.completed_at) = ? AND o.status = 'completed'
                """, (date_str,))
                
                result = cursor.fetchone()
                order_count = result[0] if result[0] else 0
                total_sales = result[1] if result[1] else 0
                avg_sales = result[2] if result[2] else 0
                

                
                # สร้างแถวข้อมูล
                row = [
                    date_str,
                    f"{total_sales:,.0f}" if total_sales > 0 else "0",
                    str(order_count)
                ]
                daily_data.append(row)
            
            # คำนวณยอดรวมทั้งหมด
            if daily_data:
                total_sales_sum = 0
                total_orders_sum = 0
                
                for row in daily_data:
                    # แปลงยอดขายจาก string กลับเป็น number
                    sales_str = row[1].replace(',', '')
                    total_sales_sum += float(sales_str) if sales_str != '0' else 0
                    total_orders_sum += int(row[2])
                
                # เพิ่มแถวยอดรวม
                summary_row = [
                    'รวมทั้งหมด',
                    f"{total_sales_sum:,.0f}",
                    str(total_orders_sum)
                ]
                daily_data.append(summary_row)
            
            conn.close()
            return daily_data
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการดึงข้อมูลยอดขายรายวัน: {e}")
            return []
    
    def get_monthly_sales_data(self) -> List[List]:
        """
        ดึงข้อมูลยอดขายรายเดือนจริงจากฐานข้อมูล
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            monthly_data = []
            today = datetime.now()
            
            # ดึงข้อมูล 6 เดือนย้อนหลัง
            for i in range(6):
                # คำนวณเดือนย้อนหลัง
                month = today.month - i
                year = today.year
                if month <= 0:
                    month += 12
                    year -= 1
                
                month_str = f"{month:02d}/{year}"
                
                # ดึงยอดขายรวมและจำนวนออเดอร์ในเดือนนั้น
                cursor.execute("""
                    SELECT 
                        COUNT(DISTINCT o.order_id) as order_count,
                        COALESCE(SUM(o.total_amount), 0) as total_sales,
                        COALESCE(AVG(o.total_amount), 0) as avg_sales
                    FROM orders o
                    WHERE strftime('%m', o.completed_at) = ? 
                    AND strftime('%Y', o.completed_at) = ? 
                    AND o.status = 'completed'
                """, (f"{month:02d}", str(year)))
                
                result = cursor.fetchone()
                order_count = result[0] if result[0] else 0
                total_sales = result[1] if result[1] else 0
                avg_sales = result[2] if result[2] else 0
                
                # ดึงเมนูขายดีในเดือนนั้น
                cursor.execute("""
                    SELECT mi.name, SUM(oi.quantity) as total_qty
                    FROM order_items oi
                    JOIN orders o ON oi.order_id = o.order_id
                    JOIN menu_items mi ON oi.item_id = mi.item_id
                    WHERE strftime('%m', o.completed_at) = ? 
                    AND strftime('%Y', o.completed_at) = ? 
                    AND o.status = 'completed'
                    GROUP BY mi.item_id, mi.name
                    ORDER BY total_qty DESC
                    LIMIT 1
                """, (f"{month:02d}", str(year)))
                
                best_item_result = cursor.fetchone()
                best_item = best_item_result[0] if best_item_result else "ไม่มีข้อมูล"
                
                # สร้างแถวข้อมูล
                row = [
                    month_str,
                    f"{total_sales:,.0f}" if total_sales > 0 else "0",
                    str(order_count),
                    f"{avg_sales:,.0f}" if avg_sales > 0 else "0",
                    best_item
                ]
                monthly_data.append(row)
            
            conn.close()
            return monthly_data
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการดึงข้อมูลยอดขายรายเดือน: {e}")
            return []
    

    
    def run(self):
        """
        รันกระบวนการเพิ่มแผ่นงานสรุปยอด
        """
        print("🚀 เริ่มต้นกระบวนการเพิ่มแผ่นงานสรุปยอด...")
        
        # ตรวจสอบแผ่นงานที่มีอยู่
        existing_sheets = self.check_existing_sheets()
        
        success_count = 0
        total_sheets = 2
        
        # สร้างแผ่นงานสรุปยอดรายวัน
        if not existing_sheets.get('Daily_Summary', False):
            if self.create_daily_summary_sheet():
                success_count += 1
        else:
            print("ℹ️ แผ่นงาน 'สรุปยอดรายวัน' มีอยู่แล้ว")
            success_count += 1
        
        # สร้างแผ่นงานสรุปยอดรายเดือน
        if not existing_sheets.get('Monthly_Summary', False):
            if self.create_monthly_summary_sheet():
                success_count += 1
        else:
            print("ℹ️ แผ่นงาน 'สรุปยอดรายเดือน' มีอยู่แล้ว")
            success_count += 1
        
        # สรุปผล
        print(f"\n📊 สรุปผลการดำเนินการ:")
        print(f"✅ สำเร็จ: {success_count}/{total_sheets} แผ่นงาน")
        
        if success_count == total_sheets:
            print("🎉 เพิ่มแผ่นงานสรุปยอดสำเร็จทั้งหมด!")
            return True
        else:
            print("⚠️ มีบางแผ่นงานที่ไม่สามารถสร้างได้")
            return False

def main():
    """
    ฟังก์ชันหลักสำหรับรันสคริปต์
    """
    try:
        print("🎯 สคริปต์เพิ่มแผ่นงานสรุปยอดรายวันและรายเดือน")
        print("=" * 60)
        
        # สร้าง instance ของ SummarySheetManager
        manager = SummarySheetManager()
        
        # รันกระบวนการ
        success = manager.run()
        
        if success:
            print("\n🎉 กระบวนการเสร็จสิ้นสำเร็จ!")
            print("📝 คุณสามารถเข้าไปดูและแก้ไขข้อมูลใน Google Sheets ได้แล้ว")
        else:
            print("\n❌ เกิดข้อผิดพลาดในกระบวนการ")
            print("🔧 กรุณาตรวจสอบการตั้งค่าและลองใหม่อีกครั้ง")
        
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⏹️ ผู้ใช้หยุดการทำงาน")
    except Exception as e:
        print(f"\n💥 เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()