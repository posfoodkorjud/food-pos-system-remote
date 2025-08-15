#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ตรวจสอบการอัปเดต Google Sheets
เพื่อยืนยันว่ายอดขายได้รับการอัปเดตด้วยเกณฑ์ใหม่แล้ว
"""

import sqlite3
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def check_google_sheets_data():
    """
    ตรวจสอบข้อมูลใน Google Sheets หลังการอัปเดต
    """
    try:
        # เชื่อมต่อ Google Sheets
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        client = gspread.authorize(creds)
        
        # เปิด spreadsheet
        spreadsheet_id = '1QzitACA2BDNwsjYm8OvTRQORYDk6QDG3nKoM5OFSpJc'
        spreadsheet = client.open_by_key(spreadsheet_id)
        
        print("=== ตรวจสอบข้อมูลใน Google Sheets ===")
        
        # ตรวจสอบแผ่น 'สรุปยอดขายรายวัน'
        try:
            daily_sheet = spreadsheet.worksheet('สรุปยอดขายรายวัน')
            daily_data = daily_sheet.get_all_records()
            
            print(f"\n📊 แผ่น 'สรุปยอดขายรายวัน': พบ {len(daily_data)} รายการ")
            
            # หายอดขายวันที่ 2025-08-12
            target_date = '2025-08-12'
            today_data = [row for row in daily_data if row.get('วันที่') == target_date]
            
            if today_data:
                for row in today_data:
                    print(f"วันที่: {row.get('วันที่')}")
                    print(f"ยอดขาย: {row.get('ยอดขาย (บาท)', 'N/A')}")
                    print(f"จำนวนออเดอร์: {row.get('จำนวนออเดอร์', 'N/A')}")
            else:
                print(f"❌ ไม่พบข้อมูลวันที่ {target_date}")
                
        except Exception as e:
            print(f"❌ ไม่สามารถเข้าถึงแผ่น 'สรุปยอดขายรายวัน': {e}")
        
        # ตรวจสอบแผ่น 'สรุปยอดขายรายเดือน'
        try:
            monthly_sheet = spreadsheet.worksheet('สรุปยอดขายรายเดือน')
            monthly_data = monthly_sheet.get_all_records()
            
            print(f"\n📊 แผ่น 'สรุปยอดขายรายเดือน': พบ {len(monthly_data)} รายการ")
            
            # หายอดขายเดือน 08/2025
            target_month = '08/2025'
            month_data = [row for row in monthly_data if row.get('เดือน/ปี') == target_month]
            
            if month_data:
                for row in month_data:
                    print(f"เดือน/ปี: {row.get('เดือน/ปี')}")
                    print(f"ยอดขาย: {row.get('ยอดขาย (บาท)', 'N/A')}")
                    print(f"จำนวนออเดอร์: {row.get('จำนวนออเดอร์', 'N/A')}")
            else:
                print(f"❌ ไม่พบข้อมูลเดือน {target_month}")
                
        except Exception as e:
            print(f"❌ ไม่สามารถเข้าถึงแผ่น 'สรุปยอดขายรายเดือน': {e}")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ Google Sheets: {e}")

def compare_database_vs_sheets():
    """
    เปรียบเทียบข้อมูลระหว่างฐานข้อมูลและ Google Sheets
    """
    print("\n=== เปรียบเทียบข้อมูลฐานข้อมูล vs Google Sheets ===")
    
    # ดึงข้อมูลจากฐานข้อมูล
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    # ยอดขายวันที่ 2025-08-12 (ทุกสถานะยกเว้น rejected)
    cursor.execute("""
        SELECT 
            COUNT(*) as order_count,
            COALESCE(SUM(total_amount), 0) as total_sales
        FROM orders 
        WHERE DATE(created_at) = '2025-08-12' 
        AND status != 'rejected'
    """)
    
    db_result = cursor.fetchone()
    db_orders = db_result[0]
    db_sales = db_result[1]
    
    print(f"📊 ฐานข้อมูล (ทุกสถานะยกเว้น rejected):")
    print(f"   จำนวนออเดอร์: {db_orders}")
    print(f"   ยอดขาย: {db_sales:,.2f} บาท")
    
    # ยอดขายวันที่ 2025-08-12 (เฉพาะ completed)
    cursor.execute("""
        SELECT 
            COUNT(*) as order_count,
            COALESCE(SUM(total_amount), 0) as total_sales
        FROM orders 
        WHERE DATE(created_at) = '2025-08-12' 
        AND status = 'completed'
    """)
    
    completed_result = cursor.fetchone()
    completed_orders = completed_result[0]
    completed_sales = completed_result[1]
    
    print(f"📊 ฐานข้อมูล (เฉพาะ completed):")
    print(f"   จำนวนออเดอร์: {completed_orders}")
    print(f"   ยอดขาย: {completed_sales:,.2f} บาท")
    
    conn.close()
    
    print(f"\n🔍 ความแตกต่าง:")
    print(f"   ออเดอร์เพิ่มเติม: {db_orders - completed_orders}")
    print(f"   ยอดขายเพิ่มเติม: {db_sales - completed_sales:,.2f} บาท")

if __name__ == "__main__":
    print("🔍 ตรวจสอบการอัปเดต Google Sheets")
    print("=" * 50)
    
    # ตรวจสอบข้อมูลใน Google Sheets
    check_google_sheets_data()
    
    # เปรียบเทียบข้อมูล
    compare_database_vs_sheets()
    
    print("\n✅ การตรวจสอบเสร็จสิ้น")