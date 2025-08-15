#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def create_new_sheets():
    """สร้างชีทใหม่ใน Google Sheets"""
    print("🚀 กำลังสร้างชีทใหม่ใน Google Sheets...")
    
    # โหลดการตั้งค่า
    with open('backend/google_sheets_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    try:
        # ตั้งค่า credentials
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = 'credentials.json'
        
        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        # สร้าง service
        print("📡 ตรวจสอบการเชื่อมต่อ Google Sheets...")
        service = build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = config['spreadsheet_id']
        
        # ดึงข้อมูลชีทที่มีอยู่
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
        print(f"📋 ชีทที่มีอยู่: {existing_sheets}")
        
        # ชีทที่ต้องการสร้าง
        required_sheets = ['Monthly_Summary', 'Item_Analytics']
        if 'sheet_names' in config:
            required_sheets.extend(list(config['sheet_names'].values()))
        print(f"📝 ชีทที่ต้องการ: {required_sheets}")
        
        # สร้างชีทใหม่ที่ยังไม่มี
        for sheet_name in required_sheets:
            if sheet_name not in existing_sheets:
                print(f"➕ กำลังสร้างชีท: {sheet_name}")
                
                # สร้างชีทใหม่
                request_body = {
                    'requests': [{
                        'addSheet': {
                            'properties': {
                                'title': sheet_name
                            }
                        }
                    }]
                }
                
                try:
                    service.spreadsheets().batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body=request_body
                    ).execute()
                    print(f"✅ สร้างชีท {sheet_name} สำเร็จ")
                    
                    # สร้างหัวตารางสำหรับชีทใหม่
                    if sheet_name == 'Monthly_Summary':
                        headers = [
                            'เดือน', 'ปี', 'ยอดขายรวม', 'จำนวนออเดอร์', 'ออเดอร์เสร็จสมบูรณ์',
                            'ออเดอร์ยกเลิก', 'อัตราความสำเร็จ (%)', 'ยอดขายเฉลี่ยต่อวัน',
                            'สินค้ายอดนิยม', 'ลูกค้าใหม่', 'ลูกค้าเก่า'
                        ]
                    elif sheet_name == 'Item_Analytics':
                        headers = [
                            'รหัสสินค้า', 'ชื่อสินค้า', 'หมวดหมู่', 'จำนวนขาย',
                            'ยอดขายรวม', 'ราคาเฉลี่ย', 'อันดับความนิยม',
                            'วันที่อัปเดตล่าสุด', 'สถานะ'
                        ]
                    elif sheet_name == 'Orders':
                        headers = [
                            'Order ID', 'Table Number', 'Order Date', 'Order Time', 
                            'Total Amount', 'Status', 'Payment Method', 'Customer Name'
                        ]
                    elif sheet_name == 'Order_Items':
                        headers = [
                            'Order ID', 'Item Name', 'Quantity', 'Unit Price', 
                            'Total Price', 'Special Options', 'Notes'
                        ]
                    elif sheet_name == 'Daily_Summary':
                        headers = [
                            'วันที่', 'วันในสัปดาห์', 'ยอดขายรวม', 'จำนวนออเดอร์', 
                            'ออเดอร์เสร็จสมบูรณ์', 'ออเดอร์ยกเลิก', 'ชั่วโมงเร่งด่วน', 'สินค้ายอดนิยม'
                        ]
                    else:
                        # ใช้หัวตารางเริ่มต้น
                        headers = ['Column A', 'Column B', 'Column C']
                    
                    # เขียนหัวตาราง
                    range_name = f"{sheet_name}!A1:{chr(65 + len(headers) - 1)}1"
                    body = {
                        'values': [headers]
                    }
                    
                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=range_name,
                        valueInputOption='RAW',
                        body=body
                    ).execute()
                    
                    print(f"📝 เพิ่มหัวตารางสำหรับ {sheet_name} สำเร็จ")
                    
                except Exception as e:
                    print(f"❌ เกิดข้อผิดพลาดในการสร้างชีท {sheet_name}: {e}")
            else:
                print(f"✅ ชีท {sheet_name} มีอยู่แล้ว")
        
        print("\n🎉 การสร้างชีทใหม่เสร็จสิ้น!")
        print(f"🔗 ลิงก์ Google Sheets: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_new_sheets()