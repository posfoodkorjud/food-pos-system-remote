import requests
import json
from datetime import datetime

# Test orders API to check if time is in local time
print("=== Testing Orders API Time Display ===")

try:
    response = requests.get('http://localhost:5000/api/orders')
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('success') and data.get('data'):
            orders = data['data']
            print(f"Total orders: {len(orders)}")
            
            print("\n=== Order Times ===")
            for i, order in enumerate(orders[:5]):  # Show first 5 orders
                print(f"Order {i+1}:")
                print(f"  Order ID: {order.get('order_id')}")
                print(f"  Created At: {order.get('created_at')}")
                print(f"  Status: {order.get('status')}")
                print(f"  Total: {order.get('total_amount')}")
                print()
                
            # Check if the time format looks like local time
            if orders:
                first_order_time = orders[0].get('created_at')
                print(f"First order time: {first_order_time}")
                
                # Try to parse the time
                try:
                    if first_order_time:
                        # Check if it's in the expected format
                        if ' ' in first_order_time and ':' in first_order_time:
                            print("✓ Time format looks correct (YYYY-MM-DD HH:MM:SS)")
                        else:
                            print("✗ Unexpected time format")
                except Exception as e:
                    print(f"Error parsing time: {e}")
        else:
            print("No orders data found")
    else:
        print(f"API Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")

print("\n=== Current Local Time ===")
print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")