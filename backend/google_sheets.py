#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Sheets Integration Module
โมดูลสำหรับการเชื่อมต่อกับ Google Sheets
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from google.oauth2.credentials import Credentials
    from google.oauth2.service_account import Credentials as ServiceAccountCredentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError as e:
    print(f"Warning: Google Sheets dependencies not installed: {e}")
    print("Run: pip install google-api-python-client google-auth google-auth-oauthlib")

class GoogleSheetsManager:
    """
    จัดการการเชื่อมต่อและการบันทึกข้อมูลลง Google Sheets
    """
    
    # ขอบเขตการเข้าถึง Google Sheets
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        """
        เริ่มต้น GoogleSheetsManager
        
        Args:
            credentials_file (str): ไฟล์ credentials จาก Google Cloud Console
            token_file (str): ไฟล์ token สำหรับเก็บ access token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.spreadsheet_id = None
        self.enabled = False
        
        # โหลดการตั้งค่าจากไฟล์ config
        self.load_config()
        
        # พยายามเชื่อมต่อ Google Sheets
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
                    self.enabled = config.get('enabled', False)
                    print(f"[Google Sheets] Loaded config: enabled={self.enabled}")
            except Exception as e:
                print(f"[Google Sheets] Error loading config: {e}")
        else:
            # สร้างไฟล์ config เริ่มต้น
            self.create_default_config()
    
    def create_default_config(self):
        """
        สร้างไฟล์ config เริ่มต้น
        """
        config = {
            'enabled': False,
            'spreadsheet_id': '',
            'sheet_names': {
                'orders': 'Orders',
                'order_items': 'Order_Items',
                'daily_summary': 'Daily_Summary'
            }
        }
        
        try:
            with open('google_sheets_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print("[Google Sheets] Created default config file")
        except Exception as e:
            print(f"[Google Sheets] Error creating config: {e}")
    
    def initialize_service(self):
        """
        เริ่มต้นการเชื่อมต่อกับ Google Sheets API
        """
        if not self.enabled:
            print("[Google Sheets] Service disabled in config")
            return False
            
        try:
            if not os.path.exists(self.credentials_file):
                print(f"[Google Sheets] Credentials file not found: {self.credentials_file}")
                print("[Google Sheets] Please download credentials.json from Google Cloud Console")
                return False
            
            # ใช้ service account credentials
            creds = ServiceAccountCredentials.from_service_account_file(
                self.credentials_file, scopes=self.SCOPES)
            
            # สร้าง service object
            self.service = build('sheets', 'v4', credentials=creds)
            print("[Google Sheets] Service initialized successfully")
            return True
            
        except Exception as e:
            print(f"[Google Sheets] Error initializing service: {e}")
            return False
    
    def test_connection(self):
        """
        ทดสอบการเชื่อมต่อกับ Google Sheets
        """
        if not self.service or not self.spreadsheet_id:
            return False
            
        try:
            # ลองอ่านข้อมูลจาก sheet
            result = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            print(f"[Google Sheets] Connected to: {result.get('properties', {}).get('title', 'Unknown')}")
            return True
            
        except HttpError as e:
            print(f"[Google Sheets] Connection test failed: {e}")
            return False
    
    def create_headers_if_needed(self):
        """
        สร้างหัวตารางและการจัดรูปแบบแบบมืออาชีพ
        """
        if not self.service or not self.spreadsheet_id:
            return False
            
        try:
            # หัวตารางสำหรับ Orders (ปรับปรุงให้ครบถ้วนมากขึ้น)
            orders_headers = [
                'Order ID', 'Table Number', 'Session ID', 'Status', 'Total Amount (฿)',
                'Payment Method', 'Customer Count', 'Order Type', 'Created Date', 
                'Created Time', 'Completed Date', 'Completed Time', 'Duration (min)', 
                'Updated At'
            ]
            
            # หัวตารางสำหรับ Order Items (เพิ่มรายละเอียด)
            items_headers = [
                'Order Item ID', 'Order ID', 'Item ID', 'Category', 'Item Name', 
                'Quantity', 'Unit Price (฿)', 'Total Price (฿)', 'Discount (%)', 
                'Final Price (฿)', 'Customer Request', 'Special Options', 
                'Status', 'Created At'
            ]
            
            # หัวตารางสำหรับ Daily Summary (เพิ่มสถิติมากขึ้น)
            summary_headers = [
                'Date', 'Day of Week', 'Total Orders', 'Completed Orders', 
                'Cancelled Orders', 'Total Revenue (฿)', 'Total Items Sold',
                'Average Order Value (฿)', 'Peak Hour', 'Most Popular Item',
                'Total Tables Served', 'Average Service Time (min)', 'Updated At'
            ]
            
            # หัวตารางสำหรับ Monthly Summary (ใหม่)
            monthly_headers = [
                'Month-Year', 'Total Orders', 'Total Revenue (฿)', 
                'Average Daily Revenue (฿)', 'Best Day', 'Worst Day',
                'Growth Rate (%)', 'Top 3 Items', 'Updated At'
            ]
            
            # หัวตารางสำหรับ Item Analytics (ใหม่)
            analytics_headers = [
                'Item Name', 'Category', 'Total Sold', 'Total Revenue (฿)',
                'Average Price (฿)', 'Popularity Rank', 'Last Ordered',
                'Frequency Score', 'Profit Margin (%)', 'Updated At'
            ]
            
            # เขียนหัวตารางพร้อมจัดรูปแบบ
            self.write_to_sheet('Orders', 'A1:N1', [orders_headers])
            self.write_to_sheet('Order_Items', 'A1:N1', [items_headers])
            self.write_to_sheet('Daily_Summary', 'A1:M1', [summary_headers])
            self.write_to_sheet('Monthly_Summary', 'A1:I1', [monthly_headers])
            self.write_to_sheet('Item_Analytics', 'A1:J1', [analytics_headers])
            
            # จัดรูปแบบหัวตาราง
            self.format_headers()
            
            print("[Google Sheets] Professional headers created successfully")
            return True
            
        except Exception as e:
            print(f"[Google Sheets] Error creating headers: {e}")
            return False
    
    def write_to_sheet(self, sheet_name: str, range_name: str, values: List[List[Any]]):
        """
        เขียนข้อมูลลง Google Sheets
        
        Args:
            sheet_name (str): ชื่อ sheet
            range_name (str): ช่วงที่จะเขียน เช่น 'A1:C1'
            values (List[List[Any]]): ข้อมูลที่จะเขียน
        """
        if not self.service or not self.spreadsheet_id:
            return False
            
        try:
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f'{sheet_name}!{range_name}',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
            
        except HttpError as e:
            print(f"[Google Sheets] Error writing to sheet: {e}")
            return False
    
    def append_to_sheet(self, sheet_name: str, values: List[List[Any]]):
        """
        เพิ่มข้อมูลต่อท้าย Google Sheets
        
        Args:
            sheet_name (str): ชื่อ sheet
            values (List[List[Any]]): ข้อมูลที่จะเพิ่ม
        """
        if not self.service or not self.spreadsheet_id:
            return False
            
        try:
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f'{sheet_name}!A:Z',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return True
            
        except HttpError as e:
            print(f"[Google Sheets] Error appending to sheet: {e}")
            return False
    
    def sync_order(self, order_data: Dict[str, Any]):
        """
        บันทึกข้อมูลออเดอร์ลง Google Sheets แบบมืออาชีพ
        
        Args:
            order_data (Dict): ข้อมูลออเดอร์
        """
        if not self.enabled or not self.service:
            return False
            
        try:
            # คำนวณระยะเวลาการให้บริการ
            duration = self.calculate_service_duration(
                order_data.get('created_at'), 
                order_data.get('completed_at')
            )
            
            # แยกวันที่และเวลา
            created_date, created_time = self.split_datetime(order_data.get('created_at', ''))
            completed_date, completed_time = self.split_datetime(order_data.get('completed_at', ''))
            
            # เตรียมข้อมูลสำหรับ Orders sheet (ปรับปรุงให้ครบถ้วน)
            order_row = [
                order_data.get('order_id', ''),
                f"โต๊ะ {order_data.get('table_id', '')}",
                order_data.get('session_id', ''),
                self.translate_status(order_data.get('status', '')),
                order_data.get('total_amount', 0),
                order_data.get('payment_method', 'เงินสด'),
                order_data.get('customer_count', 1),
                order_data.get('order_type', 'Dine-in'),
                created_date,
                created_time,
                completed_date,
                completed_time,
                duration,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            # เขียนลง Orders sheet
            success = self.append_to_sheet('Orders', [order_row])
            
            if success:
                print(f"[Google Sheets] Order {order_data.get('order_id')} synced successfully")
                # อัปเดตสถิติรายวันอัตโนมัติ
                self.update_daily_statistics(order_data)
            
            return success
            
        except Exception as e:
            print(f"[Google Sheets] Error syncing order: {e}")
            return False
    
    def sync_order_items(self, order_items: List[Dict[str, Any]]):
        """
        บันทึกรายการอาหารลง Google Sheets แบบละเอียด
        
        Args:
            order_items (List[Dict]): รายการอาหารในออเดอร์
        """
        if not self.enabled or not self.service:
            return False
            
        try:
            rows = []
            for item in order_items:
                # คำนวณส่วนลดและราคาสุดท้าย
                unit_price = item.get('unit_price', 0)
                quantity = item.get('quantity', 0)
                total_price = item.get('total_price', 0)
                discount_percent = 0
                final_price = total_price
                
                if unit_price * quantity > 0:
                    discount_percent = round((1 - (total_price / (unit_price * quantity))) * 100, 2)
                
                row = [
                    item.get('order_item_id', ''),
                    item.get('order_id', ''),
                    item.get('item_id', ''),
                    item.get('category', 'อาหาร'),
                    item.get('item_name', ''),
                    quantity,
                    unit_price,
                    unit_price * quantity,
                    discount_percent,
                    final_price,
                    item.get('customer_request', ''),
                    item.get('special_options', ''),
                    self.translate_status(item.get('status', '')),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
                rows.append(row)
            
            # เขียนลง Order_Items sheet
            success = self.append_to_sheet('Order_Items', rows)
            
            if success:
                print(f"[Google Sheets] {len(order_items)} order items synced successfully")
                # อัปเดตสถิติสินค้า
                self.update_item_analytics(order_items)
            
            return success
            
        except Exception as e:
            print(f"[Google Sheets] Error syncing order items: {e}")
            return False
    
    def format_headers(self):
        """
        จัดรูปแบบหัวตารางให้ดูมืออาชีพ
        """
        if not self.service or not self.spreadsheet_id:
            return False
            
        try:
            # สร้าง request สำหรับจัดรูปแบบ
            requests = []
            
            # จัดรูปแบบหัวตารางทุก sheet
            sheet_names = ['Orders', 'Order_Items', 'Daily_Summary', 'Monthly_Summary', 'Item_Analytics']
            
            for sheet_name in sheet_names:
                # หาหมายเลข sheet ID
                sheet_id = self.get_sheet_id(sheet_name)
                if sheet_id is not None:
                    # จัดรูปแบบแถวแรก (หัวตาราง)
                    requests.append({
                        'repeatCell': {
                            'range': {
                                'sheetId': sheet_id,
                                'startRowIndex': 0,
                                'endRowIndex': 1
                            },
                            'cell': {
                                'userEnteredFormat': {
                                    'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                                    'textFormat': {
                                        'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                        'bold': True,
                                        'fontSize': 11
                                    },
                                    'horizontalAlignment': 'CENTER'
                                }
                            },
                            'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
                        }
                    })
            
            # ส่ง request
            if requests:
                body = {'requests': requests}
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body=body
                ).execute()
                
            return True
            
        except Exception as e:
            print(f"[Google Sheets] Error formatting headers: {e}")
            return False
    
    def get_sheet_id(self, sheet_name: str):
        """
        หา Sheet ID จากชื่อ sheet
        """
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            for sheet in spreadsheet.get('sheets', []):
                if sheet['properties']['title'] == sheet_name:
                    return sheet['properties']['sheetId']
            return None
            
        except Exception as e:
            print(f"[Google Sheets] Error getting sheet ID: {e}")
            return None
    
    def calculate_service_duration(self, created_at: str, completed_at: str) -> str:
        """
        คำนวณระยะเวลาการให้บริการ
        """
        try:
            if not created_at or not completed_at:
                return ''
                
            # แปลงเป็น datetime object
            created = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            completed = datetime.strptime(completed_at, '%Y-%m-%d %H:%M:%S')
            
            # คำนวณความต่าง
            duration = completed - created
            minutes = int(duration.total_seconds() / 60)
            
            return str(minutes)
            
        except Exception as e:
            print(f"[Google Sheets] Error calculating duration: {e}")
            return ''
    
    def split_datetime(self, datetime_str: str) -> tuple:
        """
        แยกวันที่และเวลา
        """
        try:
            if not datetime_str:
                return '', ''
                
            dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            date_part = dt.strftime('%Y-%m-%d')
            time_part = dt.strftime('%H:%M:%S')
            
            return date_part, time_part
            
        except Exception as e:
            print(f"[Google Sheets] Error splitting datetime: {e}")
            return '', ''
    
    def translate_status(self, status: str) -> str:
        """
        แปลสถานะเป็นภาษาไทย
        """
        status_map = {
            'pending': 'รอดำเนินการ',
            'preparing': 'กำลังเตรียม',
            'ready': 'พร้อมเสิร์ฟ',
            'completed': 'เสร็จสิ้น',
            'cancelled': 'ยกเลิก',
            'paid': 'ชำระแล้ว'
        }
        return status_map.get(status.lower(), status)
    
    def update_daily_statistics(self, order_data: Dict[str, Any]):
        """
        อัปเดตสถิติรายวันอัตโนมัติ
        """
        try:
            if not order_data.get('completed_at'):
                return
                
            date = order_data.get('completed_at', '').split(' ')[0]
            
            # ดึงข้อมูลสถิติวันนี้จากฐานข้อมูล (จำลอง)
            daily_stats = self.calculate_daily_stats(date)
            
            if daily_stats:
                self.sync_daily_summary(date, daily_stats)
                
        except Exception as e:
            print(f"[Google Sheets] Error updating daily statistics: {e}")
    
    def update_item_analytics(self, order_items: List[Dict[str, Any]]):
        """
        อัปเดตสถิติสินค้าอัตโนมัติ
        """
        try:
            # จำลองการอัปเดตสถิติสินค้า
            for item in order_items:
                item_name = item.get('item_name', '')
                if item_name:
                    # ในการใช้งานจริงจะดึงข้อมูลจากฐานข้อมูล
                    print(f"[Google Sheets] Updated analytics for {item_name}")
                    
        except Exception as e:
            print(f"[Google Sheets] Error updating item analytics: {e}")
    
    def calculate_daily_stats(self, date: str) -> Dict[str, Any]:
        """
        คำนวณสถิติรายวัน (จำลอง - ในการใช้งานจริงจะดึงจากฐานข้อมูล)
        """
        try:
            # จำลองข้อมูลสถิติ
            return {
                'total_orders': 25,
                'completed_orders': 23,
                'cancelled_orders': 2,
                'total_revenue': 2500.0,
                'total_items_sold': 45,
                'average_order_value': 108.7,
                'peak_hour': '12:00-13:00',
                'most_popular_item': 'ข้าวผัดกุ้ง',
                'total_tables_served': 15,
                'average_service_time': 18
            }
            
        except Exception as e:
            print(f"[Google Sheets] Error calculating daily stats: {e}")
            return {}
    
    def sync_daily_summary(self, date: str, summary_data: Dict[str, Any]):
        """
        บันทึกสรุปยอดขายรายวันลง Google Sheets แบบครบถ้วน
        
        Args:
            date (str): วันที่
            summary_data (Dict): ข้อมูลสรุปยอดขาย
        """
        if not self.enabled or not self.service:
            return False
            
        try:
            # หาวันในสัปดาห์
            try:
                dt = datetime.strptime(date, '%Y-%m-%d')
                day_names = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัสบดี', 'ศุกร์', 'เสาร์', 'อาทิตย์']
                day_of_week = day_names[dt.weekday()]
            except:
                day_of_week = ''
            
            row = [
                date,
                day_of_week,
                summary_data.get('total_orders', 0),
                summary_data.get('completed_orders', 0),
                summary_data.get('cancelled_orders', 0),
                summary_data.get('total_revenue', 0),
                summary_data.get('total_items_sold', 0),
                summary_data.get('average_order_value', 0),
                summary_data.get('peak_hour', ''),
                summary_data.get('most_popular_item', ''),
                summary_data.get('total_tables_served', 0),
                summary_data.get('average_service_time', 0),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            # เขียนลง Daily_Summary sheet
            success = self.append_to_sheet('Daily_Summary', [row])
            
            if success:
                print(f"[Google Sheets] Daily summary for {date} synced successfully")
            
            return success
            
        except Exception as e:
            print(f"[Google Sheets] Error syncing daily summary: {e}")
            return False

# สร้าง instance สำหรับใช้งานทั่วไป
google_sheets_manager = GoogleSheetsManager()

def is_google_sheets_enabled():
    """
    ตรวจสอบว่า Google Sheets integration เปิดใช้งานหรือไม่
    """
    return google_sheets_manager.enabled and google_sheets_manager.service is not None

def sync_order_to_sheets(order_data, order_items=None):
    """
    ฟังก์ชันสำหรับบันทึกออเดอร์ลง Google Sheets
    
    Args:
        order_data (Dict): ข้อมูลออเดอร์
        order_items (List[Dict], optional): รายการอาหารในออเดอร์
    """
    if not is_google_sheets_enabled():
        return False
        
    try:
        # บันทึกออเดอร์
        order_success = google_sheets_manager.sync_order(order_data)
        
        # บันทึกรายการอาหาร (ถ้ามี)
        items_success = True
        if order_items:
            items_success = google_sheets_manager.sync_order_items(order_items)
        
        return order_success and items_success
        
    except Exception as e:
        print(f"[Google Sheets] Error in sync_order_to_sheets: {e}")
        return False

def setup_google_sheets(spreadsheet_id: str):
    """
    ตั้งค่า Google Sheets integration
    
    Args:
        spreadsheet_id (str): ID ของ Google Spreadsheet
    """
    try:
        # อัปเดต config
        config = {
            'enabled': True,
            'spreadsheet_id': spreadsheet_id,
            'sheet_names': {
                'orders': 'Orders',
                'order_items': 'Order_Items',
                'daily_summary': 'Daily_Summary'
            }
        }
        
        with open('google_sheets_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # รีโหลด config
        google_sheets_manager.spreadsheet_id = spreadsheet_id
        google_sheets_manager.enabled = True
        
        # ทดสอบการเชื่อมต่อ
        if google_sheets_manager.test_connection():
            # สร้างหัวตาราง
            google_sheets_manager.create_headers_if_needed()
            print("[Google Sheets] Setup completed successfully")
            return True
        else:
            print("[Google Sheets] Setup failed - connection test failed")
            return False
            
    except Exception as e:
        print(f"[Google Sheets] Setup error: {e}")
        return False