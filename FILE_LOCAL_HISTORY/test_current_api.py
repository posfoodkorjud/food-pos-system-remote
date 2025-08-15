import requests
import json
from datetime import datetime

# Test the current API
base_url = "http://localhost:5000"

# Get today's date
today = datetime.now().strftime('%Y-%m-%d')
print(f"Today's date: {today}")

# Test dashboard data API
print("\n=== Testing Dashboard API ===")
try:
    response = requests.get(f"{base_url}/api/dashboard-data", params={
        'start_date': today,
        'end_date': today
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
        print(f"Today Sales: {api_data.get('todaySales', 'N/A')}")
        print(f"Period Sales: {api_data.get('periodSales', 'N/A')}")
        print(f"Week Sales: {api_data.get('weekSales', 'N/A')}")
        print(f"Month Sales: {api_data.get('monthSales', 'N/A')}")
        print(f"Today Orders: {api_data.get('todayOrders', 'N/A')}")
        print(f"Total Orders: {api_data.get('totalOrders', 'N/A')}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error connecting to API: {e}")

# Test orders API
print("\n=== Testing Orders API ===")
try:
    response = requests.get(f"{base_url}/api/orders")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        orders = response.json()
        print(f"Total orders returned: {len(orders)}")
        
        # Show last 3 orders
        if orders:
            print("\nLast 3 orders:")
            for order in orders[-3:]:
                print(f"Order ID: {order.get('order_id')}, Amount: {order.get('total_amount')}, Date: {order.get('created_at')}, Status: {order.get('status')}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error connecting to orders API: {e}")