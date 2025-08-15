#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับอัปเดตข้อมูลในแผ่นงานสรุปยอดที่มีอยู่แล้ว
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

class SummaryDataUpdater:
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
        """โหลดการตั้งค่าจากไฟล์ config"""
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
            sys.exit(1)
    
    def initialize_service(self):
        """เริ่มต้น Google Sheets service"""
        try:
            if not os.path.exists(self.credentials_file):
                print(f"❌ ไม่พบไฟล์ {self.credentials_file}")
                return False
            
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            self.service = build('sheets', 'v4', credentials=credentials)
            print("✅ เชื่อมต่อ Google Sheets API สำเร็จ")
            return True
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการเชื่อมต่อ Google Sheets API: {e}")
            return False
    
    def clear_sheet_data(self, sheet_name: str, start_row: int = 2):
        """ล้างข้อมูลในแผ่นงาน (เก็บส่วนหัวไว้)"""
        try:
            # ล้างข้อมูลตั้งแต่แถวที่ 2 (เก็บส่วนหัวไว้)
            range_name = f"{sheet_name}!A{start_row}:Z1000"
            
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            print(f"🧹 ล้างข้อมูลใน {sheet_name} สำเร็จ")
            return True
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการล้างข้อมูล {sheet_name}: {e}")
            return False
    
    def write_header_to_sheet(self, sheet_name: str):
        """เขียน header ลงแผ่นงาน"""
        try:
            headers = [
                ['วันที่', 'ยอดขาย', 'จำนวนบิล']
            ]
            range_name = f"{sheet_name}!A1"
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body={'values': headers}
            ).execute()
            print(f"✅ เขียน header ลง {sheet_name} สำเร็จ")
            return True
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการเขียน header: {e}")
            return False
    
    def write_to_sheet(self, sheet_name: str, data: List[List], range_start: str = 'A2'):
        """เขียนข้อมูลลงแผ่นงาน"""
        try:
            if not data:
                print(f"⚠️ ไม่มีข้อมูลสำหรับ {sheet_name}")
                return False
            
            range_name = f"{sheet_name}!{range_start}"
            
            body = {
                'values': data
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ เขียนข้อมูลลง {sheet_name} สำเร็จ ({len(data)} แถว)")
            return True
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการเขียนข้อมูลลง {sheet_name}: {e}")
            return False
    
    def get_daily_sales_data(self) -> List[List]:
        """ดึงข้อมูลยอดขายรายวันจริงจากฐานข้อมูล (ทุกวัน พร้อมแถวสรุปยอดแต่ละเดือน)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            daily_data = []

            # ดึงวันที่ทั้งหมดที่มีออเดอร์ (ยกเว้น rejected)
            cursor.execute("""
                SELECT DISTINCT DATE(o.created_at)
                FROM orders o
                WHERE o.status != 'rejected'
                ORDER BY DATE(o.created_at) ASC
            """)
            date_rows = cursor.fetchall()
            date_list = [row[0] for row in date_rows]

            current_month = None
            month_sales_sum = 0
            month_orders_sum = 0
            monthly_rows = []
            all_data = []

            for date_str in date_list:
                if not date_str:
                    continue
                # ดึงยอดขายรวมและจำนวนออเดอร์ในวันนั้น
                cursor.execute("""
                    SELECT 
                        COUNT(DISTINCT o.order_id) as order_count,
                        COALESCE(SUM(o.total_amount), 0) as total_sales,
                        COALESCE(AVG(o.total_amount), 0) as avg_sales
                    FROM orders o
                    WHERE DATE(o.created_at) = ? AND o.status != 'rejected'
                """, (date_str,))
                result = cursor.fetchone()
                order_count = result[0] if result[0] else 0
                total_sales = result[1] if result[1] else 0
                avg_sales = result[2] if result[2] else 0
                row = [
                    date_str,
                    f"{total_sales:,.0f}" if total_sales > 0 else "0",
                    str(order_count)
                ]
                # ตรวจสอบเดือน
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                month_key = date_obj.strftime("%m/%Y")
                if current_month is None:
                    current_month = month_key
                if month_key != current_month:
                    # เพิ่มแถวสรุปยอดเดือนก่อนหน้า
                    summary_row = [
                        f"รวม {current_month}",
                        f"{month_sales_sum:,.0f}",
                        str(month_orders_sum)
                    ]
                    all_data.extend(monthly_rows)
                    all_data.append(summary_row)
                    # reset
                    monthly_rows = []
                    month_sales_sum = 0
                    month_orders_sum = 0
                    current_month = month_key
                monthly_rows.append(row)
                # สะสมยอด
                sales_str = row[1].replace(',', '')
                month_sales_sum += float(sales_str) if sales_str != '0' else 0
                month_orders_sum += int(row[2])
            # เพิ่มแถวสรุปเดือนสุดท้าย
            if monthly_rows:
                summary_row = [
                    f"รวม {current_month}",
                    f"{month_sales_sum:,.0f}",
                    str(month_orders_sum)
                ]
                all_data.extend(monthly_rows)
                all_data.append(summary_row)
            # คำนวณยอดรวมทั้งหมด
            if all_data:
                total_sales_sum = 0
                total_orders_sum = 0
                for row in all_data:
                    if row[0].startswith('รวม '):
                        continue
                    sales_str = row[1].replace(',', '')
                    total_sales_sum += float(sales_str) if sales_str != '0' else 0
                    total_orders_sum += int(row[2])
                summary_row = [
                    'รวมทั้งหมด',
                    f"{total_sales_sum:,.0f}",
                    str(total_orders_sum)
                ]
                all_data.append(summary_row)
            conn.close()
            return all_data
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการดึงข้อมูลยอดขายรายวัน: {e}")
            return []
    
    def get_monthly_sales_data(self) -> List[List]:
        """ดึงข้อมูลยอดขายรายเดือนจริงจากฐานข้อมูล (พร้อมแถวสรุปยอดรวมทุกเดือน)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            monthly_data = []
            # ดึงเดือนและปีทั้งหมดที่มีออเดอร์ (ยกเว้น rejected)
            cursor.execute("""
                SELECT DISTINCT strftime('%m', o.created_at) as m, strftime('%Y', o.created_at) as y
                FROM orders o
                WHERE o.status != 'rejected'
                ORDER BY y ASC, m ASC
            """)
            month_rows = cursor.fetchall()
            total_sales_sum = 0
            total_orders_sum = 0
            for m, y in month_rows:
                month_str = f"{m}/{y}"
                # ดึงยอดขายรวมและจำนวนออเดอร์ในเดือนนั้น
                cursor.execute("""
                    SELECT 
                        COUNT(DISTINCT o.order_id) as order_count,
                        COALESCE(SUM(o.total_amount), 0) as total_sales,
                        COALESCE(AVG(o.total_amount), 0) as avg_sales
                    FROM orders o
                    WHERE strftime('%m', o.created_at) = ? 
                    AND strftime('%Y', o.created_at) = ? 
                    AND o.status != 'rejected'
                """, (m, y))
                result = cursor.fetchone()
                order_count = result[0] if result[0] else 0
                total_sales = result[1] if result[1] else 0
                avg_sales = result[2] if result[2] else 0
                total_sales_sum += total_sales
                total_orders_sum += order_count
                # ดึงเมนูขายดีในเดือนนั้น
                cursor.execute("""
                    SELECT mi.name, SUM(oi.quantity) as total_qty
                    FROM order_items oi
                    JOIN orders o ON oi.order_id = o.order_id
                    JOIN menu_items mi ON oi.item_id = mi.item_id
                    WHERE strftime('%m', o.created_at) = ? 
                    AND strftime('%Y', o.created_at) = ? 
                    AND o.status != 'rejected'
                    GROUP BY mi.item_id, mi.name
                    ORDER BY total_qty DESC
                    LIMIT 1
                """, (m, y))
                best_item_result = cursor.fetchone()
                best_item = best_item_result[0] if best_item_result else "ไม่มีข้อมูล"
                row = [
                    month_str,
                    f"{total_sales:,.0f}" if total_sales > 0 else "0",
                    str(order_count),
                    f"{avg_sales:,.0f}" if avg_sales > 0 else "0",
                    best_item
                ]
                monthly_data.append(row)
            # เพิ่มแถวสรุปยอดรวมทุกเดือน
            if monthly_data:
                summary_row = [
                    'รวมทั้งหมด',
                    f"{total_sales_sum:,.0f}",
                    str(total_orders_sum),
                    '',
                    ''
                ]
                monthly_data.append(summary_row)
            conn.close()
            return monthly_data
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการดึงข้อมูลยอดขายรายเดือน: {e}")
            return []
    
    def format_daily_summary_sheet(self):
        """จัดรูปแบบแผ่นงาน Daily_Summary ให้ดูเรียบร้อย (เน้นแถวสรุป, เว้นบรรทัด, สีพื้นหลัง)"""
        import re
        try:
            requests = []
            sheet_name = 'Daily_Summary'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{sheet_name}!A1:C1000'
            ).execute()
            values = result.get('values', [])
            summary_month_rows = []
            summary_total_row = None
            
            # Debug: แสดงข้อมูลที่อ่านได้จาก Google Sheets
            print("🔍 Debug: ข้อมูลใน Google Sheets:")
            for idx, row in enumerate(values[:20]):  # แสดงแค่ 20 แถวแรก
                if row:
                    print(f"แถวที่ {idx+1}: '{row[0].strip()}' (ความยาว: {len(row[0].strip())})")
                    if re.match(r'^รวม\s+\d{2}/\d{4}$', row[0].strip()):
                        print(f"  ✅ ตรงกับ regex pattern (แถวสรุปเดือน)")
                        summary_month_rows.append(idx)
                    elif row[0].strip() == 'รวมทั้งหมด':
                        print(f"  ✅ ตรงกับแถวรวมทั้งหมด")
                        summary_total_row = idx
                    else:
                        print(f"  ❌ ไม่ตรงกับ pattern ใดๆ")
            
            print(f"🎯 พบแถวสรุปเดือน: {summary_month_rows}")
            print(f"🎯 พบแถวรวมทั้งหมด: {summary_total_row}")
            
            # จัดรูปแบบหัวตาราง
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 1},
                            'horizontalAlignment': 'CENTER',
                            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
                }
            })
            # จัดรูปแบบแถวสรุปยอดแต่ละเดือน (เหลือง)
            for idx in summary_month_rows:
                print(f"🎨 จัดรูปแบบแถวที่ {idx+1} เป็นสีเหลือง")
                requests.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': idx,
                            'endRowIndex': idx+1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 1, 'green': 0.92, 'blue': 0.6},
                                'textFormat': {'bold': True}
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                })
            # จัดรูปแบบแถวรวมทั้งหมด (ฟ้าอ่อน)
            if summary_total_row is not None:
                print(f"🎨 จัดรูปแบบแถวที่ {summary_total_row+1} เป็นสีฟ้าอ่อน")
                requests.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': summary_total_row,
                            'endRowIndex': summary_total_row+1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 0.8, 'green': 0.9, 'blue': 1},
                                'textFormat': {'bold': True}
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                })
            body = {'requests': requests}
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            # เว้นบรรทัดหลังแถวสรุปแต่ละเดือน (ยกเว้นรวมทั้งหมด) หลังจัด format สี
            for idx in reversed(summary_month_rows):
                if idx+1 < len(values) and not (values[idx+1][0].strip() == 'รวมทั้งหมด'):
                    print(f"📝 แทรกแถวว่างหลังแถวที่ {idx+1}")
                    self.service.spreadsheets().batchUpdate(
                        spreadsheetId=self.spreadsheet_id,
                        body={
                            'requests': [{
                                'insertDimension': {
                                    'range': {
                                        'sheetId': 0,
                                        'dimension': 'ROWS',
                                        'startIndex': idx+1,
                                        'endIndex': idx+2
                                    },
                                    'inheritFromBefore': False
                                }
                            }]
                        }
                    ).execute()
            print('✅ จัดรูปแบบ Daily_Summary เรียบร้อย')
        except Exception as e:
            print(f'❌ ข้อผิดพลาดในการจัดรูปแบบ Daily_Summary: {e}')
    
    def update_daily_summary(self):
        """อัปเดตข้อมูลยอดขายรายวันใน Daily_Summary"""
        self.clear_sheet_data('Daily_Summary', start_row=2)
        self.write_header_to_sheet('Daily_Summary')
        daily_data = self.get_daily_sales_data()
        self.write_to_sheet('Daily_Summary', daily_data, range_start='A2')
        self.format_daily_summary_sheet()
    
    def update_monthly_summary(self):
        """อัปเดตข้อมูลสรุปยอดรายเดือน"""
        print("🔄 กำลังอัปเดตข้อมูลสรุปยอดรายเดือน...")
        
        # ล้างข้อมูลเก่า (เก็บส่วนหัวไว้)
        if not self.clear_sheet_data('Daily_Summary', 2):
            return False
        
        # ดึงข้อมูลใหม่
        daily_data = self.get_daily_sales_data()
        if not daily_data:
            print("⚠️ ไม่มีข้อมูลยอดขายรายวัน")
            return False
        
        # เขียนข้อมูลใหม่
        return self.write_to_sheet('Daily_Summary', daily_data)
    
    def update_monthly_summary(self):
        """อัปเดตข้อมูลสรุปยอดรายเดือน"""
        print("🔄 กำลังอัปเดตข้อมูลสรุปยอดรายเดือน...")
        
        # ล้างข้อมูลเก่า (เก็บส่วนหัวไว้)
        if not self.clear_sheet_data('Monthly_Summary', 2):
            return False
        
        # ดึงข้อมูลใหม่
        monthly_data = self.get_monthly_sales_data()
        if not monthly_data:
            print("⚠️ ไม่มีข้อมูลยอดขายรายเดือน")
            return False
        
        # เขียนข้อมูลใหม่
        return self.write_to_sheet('Monthly_Summary', monthly_data)
    
    def run(self):
        """รันกระบวนการอัปเดตข้อมูล"""
        print("🚀 เริ่มต้นกระบวนการอัปเดตข้อมูลสรุปยอด...")
        
        success_count = 0
        total_updates = 2
        
        # อัปเดตข้อมูลสรุปยอดรายวัน
        if self.update_daily_summary():
            success_count += 1
        
        # อัปเดตข้อมูลสรุปยอดรายเดือน
        if self.update_monthly_summary():
            success_count += 1
        
        # สรุปผล
        print(f"\n📊 สรุปผลการอัปเดต:")
        print(f"✅ สำเร็จ: {success_count}/{total_updates} แผ่นงาน")
        
        if success_count == total_updates:
            print("🎉 อัปเดตข้อมูลสำเร็จทั้งหมด!")
            return True
        else:
            print("⚠️ มีบางแผ่นงานที่ไม่สามารถอัปเดตได้")
            return False

def main():
    """ฟังก์ชันหลักสำหรับรันสคริปต์"""
    try:
        print("🎯 สคริปต์อัปเดตข้อมูลสรุปยอดรายวันและรายเดือน")
        print("=" * 60)
        
        # สร้าง instance ของ SummaryDataUpdater
        updater = SummaryDataUpdater()
        
        # รันกระบวนการ
        success = updater.run()
        
        if success:
            print("\n🎉 กระบวนการอัปเดตเสร็จสิ้นสำเร็จ!")
            print("📝 ข้อมูลใน Google Sheets ได้รับการอัปเดตแล้ว")
        else:
            print("\n❌ เกิดข้อผิดพลาดในกระบวนการอัปเดต")
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