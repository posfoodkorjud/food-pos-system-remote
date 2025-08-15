#!/usr/bin/env python3
import webbrowser
import json

# อ่าน config
with open('google_sheets_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

spreadsheet_id = config['spreadsheet_id']
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid=0"

print(f"🌐 เปิด Google Sheets: {url}")
webbrowser.open(url)
print("✅ เปิด Google Sheets เรียบร้อยแล้ว!")