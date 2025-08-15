import requests
import json
from datetime import datetime

# Test the updated customer count API
base_url = "http://localhost:5000"

# Get today's date
today = datetime.now().strftime('%Y-%m-%d')
print(f"Testing customer count for date: {today}")

# Test dashboard data API
print("\n=== Testing Updated Customer Count API ===")
try:
    response = requests.get(f"{base_url}/api/dashboard-data", params={
        'start': today,
        'end': today
    })
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("\nFull API Response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Extract key values
        if 'data' in data:
            api_data = data['data']
        else:
            api_data = data
            
        print("\n=== Key Values ===")
        print(f"Total Customers (เฉพาะที่สั่งอาหาร): {api_data.get('totalCustomers', 'N/A')}")
        print(f"Total Orders: {api_data.get('totalOrders', 'N/A')}")
        print(f"Period Sales: {api_data.get('periodSales', 'N/A')}")
        print(f"Today Sales: {api_data.get('todaySales', 'N/A')}")
        
        print("\n=== Explanation ===")
        print("ตอนนี้ระบบจะนับเฉพาะโต๊ะที่มีการสั่งอาหารเข้ามาแล้ว")
        print("ไม่นับโต๊ะที่เปิดเซสชั่นแล้วแต่ยังไม่ได้สั่งอาหาร")
        
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error connecting to API: {e}")