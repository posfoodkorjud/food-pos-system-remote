import requests
import json
from datetime import datetime, timedelta

# Test the dashboard API
print("=== Testing Week Sales Calculation ===")
print(f"Today's date: {datetime.now().strftime('%Y-%m-%d')}")

# Calculate current week (Monday to Sunday)
today = datetime.now()
days_since_monday = today.weekday()  # Monday = 0, Sunday = 6
week_start = today - timedelta(days=days_since_monday)
week_end = week_start + timedelta(days=6)

print(f"Current week should be: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")

# Test dashboard API
try:
    response = requests.get('http://localhost:5000/api/dashboard-data')
    if response.status_code == 200:
        data = response.json()
        print(f"\nAPI Response:")
        print(f"Today Sales: {data['data']['todaySales']}")
        print(f"Week Sales: {data['data']['weekSales']}")
        print(f"Period Sales: {data['data']['periodSales']}")
        print(f"Month Sales: {data['data']['monthSales']}")
    else:
        print(f"API Error: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")

# Test with 7-day period
print("\n=== Testing 7-day Period Sales ===")
start_date = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')
print(f"7-day period: {start_date} to {end_date}")

try:
    response = requests.get(f'http://localhost:5000/api/dashboard-data?start_date={start_date}&end_date={end_date}')
    if response.status_code == 200:
        data = response.json()
        print(f"Period Sales (7 days): {data['data']['periodSales']}")
        print(f"Week Sales (current week): {data['data']['weekSales']}")
    else:
        print(f"API Error: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")