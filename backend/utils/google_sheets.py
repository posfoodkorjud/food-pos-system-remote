# -*- coding: utf-8 -*-
"""
Google Sheets Integration สำหรับระบบ POS
"""

import os
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

try:
    from googleapiclient.discovery import build
    from google.oauth2.service_account import Credentials
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Warning: Google API libraries not installed. Google Sheets integration will be disabled.")

class GoogleSheetsManager:
    """คลาสจัดการ Google Sheets API"""
    
    def __init__(self, credentials_file: str = "credentials.json"):
        self.credentials_file = credentials_file
        self.service = None
        self.sheet_id = None
        self.sheet_name = "ยอดขาย"
        self.enabled = False
        
        # โหลดการตั้งค่าจากไฟล์ config
        self._load_config()
        
        if GOOGLE_AVAILABLE and self.enabled:
            self._initialize_service()
    
    def _load_config(self):
        """
        โหลดการตั้งค่าจากไฟล์ config
        """
        config_file = 'google_sheets_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.sheet_id = config.get('spreadsheet_id')
                    self.enabled = config.get('enabled', False)
                    print(f"[Google Sheets] Loaded config: enabled={self.enabled}, sheet_id={self.sheet_id}")
            except Exception as e:
                print(f"[Google Sheets] Error loading config: {e}")
        else:
            print(f"[Google Sheets] Config file not found: {config_file}")
    
    def _initialize_service(self):
        """
        เริ่มต้นการเชื่อมต่อ Google Sheets API
        """
        try:
            if not os.path.exists(self.credentials_file):
                print(f"Credentials file not found: {self.credentials_file}")
                return
            
            # กำหนด scope ที่ต้องการ
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            
            # สร้าง credentials
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=scopes
            )
            
            # สร้าง service
            self.service = build('sheets', 'v4', credentials=credentials)
            print("Google Sheets service initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Google Sheets service: {e}")
            self.service = None
    
    def set_sheet_config(self, sheet_id: str, sheet_name: str = "ยอดขาย"):
        """
        ตั้งค่า Google Sheet ID และชื่อแท็บ
        
        Args:
            sheet_id: Google Sheet ID
            sheet_name: ชื่อแท็บในชีต
        """
        self.sheet_id = sheet_id
        self.sheet_name = sheet_name
    
    def test_connection(self) -> bool:
        """
        ทดสอบการเชื่อมต่อ Google Sheets
        
        Returns:
            True ถ้าเชื่อมต่อได้, False ถ้าไม่ได้
        """
        if not GOOGLE_AVAILABLE or not self.service or not self.sheet_id:
            return False
        
        try:
            # ลองอ่านข้อมูลจากชีต
            result = self.service.spreadsheets().get(
                spreadsheetId=self.sheet_id
            ).execute()
            
            print(f"Connected to sheet: {result.get('properties', {}).get('title', 'Unknown')}")
            return True
            
        except Exception as e:
            print(f"Error testing Google Sheets connection: {e}")
            return False
    
    def create_headers_if_needed(self) -> bool:
        """
        สร้างหัวตารางในชีตถ้ายังไม่มี
        
        Returns:
            True ถ้าสำเร็จ, False ถ้าล้มเหลว
        """
        if not self.service or not self.sheet_id:
            return False
        
        try:
            # ตรวจสอบว่ามีข้อมูลในแถวแรกหรือไม่
            range_name = f"{self.sheet_name}!A1:Z1"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # ถ้าไม่มีข้อมูลในแถวแรก ให้สร้างหัวตาราง
            if not values or not values[0]:
                headers = [
                    'วันที่',
                    'เวลา',
                    'โต๊ะ',
                    'Session ID',
                    'รายการอาหาร',
                    'จำนวน',
                    'ราคาต่อหน่วย',
                    'ราคารวม',
                    'ยอดรวมทั้งหมด',
                    'สถานะ'
                ]
                
                body = {
                    'values': [headers]
                }
                
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.sheet_id,
                    range=f"{self.sheet_name}!A1",
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                print("Headers created in Google Sheet")
            
            return True
            
        except Exception as e:
            print(f"Error creating headers: {e}")
            return False
    
    def send_sales_data(self, receipt_data: Dict) -> bool:
        """
        ส่งข้อมูลยอดขายไป Google Sheets
        
        Args:
            receipt_data: ข้อมูลใบเสร็จ
            
        Returns:
            True ถ้าส่งสำเร็จ, False ถ้าล้มเหลว
        """
        if not GOOGLE_AVAILABLE or not self.service or not self.sheet_id:
            print("Google Sheets not available or not configured")
            return False
        
        try:
            # สร้างหัวตารางถ้าจำเป็น
            self.create_headers_if_needed()
            
            # เตรียมข้อมูลสำหรับส่ง
            rows = []
            
            created_at = datetime.fromisoformat(receipt_data['created_at'].replace('Z', '+00:00'))
            date_str = created_at.strftime('%Y-%m-%d')
            time_str = created_at.strftime('%H:%M:%S')
            
            # สร้างแถวข้อมูลสำหรับแต่ละรายการอาหาร
            for order in receipt_data['orders']:
                row = [
                    date_str,
                    time_str,
                    f"โต๊ะ {receipt_data['table_id']}",
                    receipt_data['session_id'],
                    order['item_name'],
                    order['quantity'],
                    order['unit_price'],
                    order['total_price'],
                    receipt_data['total_amount'],
                    'ชำระแล้ว'
                ]
                rows.append(row)
            
            # ถ้าไม่มีรายการอาหาร ให้สร้างแถวเดียว
            if not rows:
                row = [
                    date_str,
                    time_str,
                    f"โต๊ะ {receipt_data['table_id']}",
                    receipt_data['session_id'],
                    'ไม่มีรายการ',
                    0,
                    0,
                    0,
                    receipt_data['total_amount'],
                    'ชำระแล้ว'
                ]
                rows.append(row)
            
            # ส่งข้อมูลไปยัง Google Sheets
            body = {
                'values': rows
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=f"{self.sheet_name}!A:J",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            print(f"Successfully sent {len(rows)} rows to Google Sheets")
            return True
            
        except Exception as e:
            print(f"Error sending data to Google Sheets: {e}")
            return False
    
    def get_daily_sales(self, date: str = None) -> List[Dict]:
        """
        ดึงข้อมูลยอดขายรายวัน
        
        Args:
            date: วันที่ในรูปแบบ YYYY-MM-DD (ถ้าไม่ระบุจะใช้วันนี้)
            
        Returns:
            รายการข้อมูลยอดขาย
        """
        if not self.service or not self.sheet_id:
            return []
        
        try:
            if not date:
                date = datetime.now(timezone(timedelta(hours=7))).strftime('%Y-%m-%d')
            
            # อ่านข้อมูลทั้งหมดจากชีต
            range_name = f"{self.sheet_name}!A:J"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return []
            
            # กรองข้อมูลตามวันที่
            daily_sales = []
            headers = values[0] if values else []
            
            for row in values[1:]:  # ข้าม header
                if len(row) > 0 and row[0] == date:
                    sale_data = {}
                    for i, header in enumerate(headers):
                        sale_data[header] = row[i] if i < len(row) else ''
                    daily_sales.append(sale_data)
            
            return daily_sales
            
        except Exception as e:
            print(f"Error getting daily sales: {e}")
            return []
    
    def get_monthly_summary(self, year: int = None, month: int = None) -> Dict:
        """
        ดึงสรุปยอดขายรายเดือน
        
        Args:
            year: ปี (ถ้าไม่ระบุจะใช้ปีนี้)
            month: เดือน (ถ้าไม่ระบุจะใช้เดือนนี้)
            
        Returns:
            สรุปยอดขายรายเดือน
        """
        if not self.service or not self.sheet_id:
            return {}
        
        try:
            now = datetime.now(timezone(timedelta(hours=7)))
            if not year:
                year = now.year
            if not month:
                month = now.month
            
            # อ่านข้อมูลทั้งหมดจากชีต
            range_name = f"{self.sheet_name}!A:J"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return {}
            
            # คำนวณสรุปยอดขาย
            total_sales = 0
            total_orders = 0
            daily_sales = {}
            
            for row in values[1:]:  # ข้าม header
                if len(row) > 0:
                    try:
                        date_str = row[0]
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        
                        if date_obj.year == year and date_obj.month == month:
                            amount = float(row[8]) if len(row) > 8 and row[8] else 0
                            total_sales += amount
                            total_orders += 1
                            
                            day = date_obj.day
                            if day not in daily_sales:
                                daily_sales[day] = 0
                            daily_sales[day] += amount
                            
                    except (ValueError, IndexError):
                        continue
            
            return {
                'year': year,
                'month': month,
                'total_sales': total_sales,
                'total_orders': total_orders,
                'average_per_order': total_sales / total_orders if total_orders > 0 else 0,
                'daily_sales': daily_sales
            }
            
        except Exception as e:
            print(f"Error getting monthly summary: {e}")
            return {}

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    # ทดสอบการเชื่อมต่อ
    sheets_manager = GoogleSheetsManager()
    
    # ตั้งค่าชีต (ต้องมี Google Sheet ID จริง)
    # sheets_manager.set_sheet_config("your_sheet_id_here")
    
    # ทดสอบการเชื่อมต่อ
    # connected = sheets_manager.test_connection()
    # print(f"Connection test: {connected}")
    
    print("Google Sheets manager initialized")
    print(f"Google API available: {GOOGLE_AVAILABLE}")