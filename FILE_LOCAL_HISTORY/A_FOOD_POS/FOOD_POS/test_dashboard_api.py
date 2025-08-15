import requests
import json
from datetime import datetime, timedelta

def test_dashboard_api():
    """Test dashboard API with 30 days range"""
    
    # Calculate 30 days range (same as frontend)
    today = datetime.now()
    start_date = today - timedelta(days=29)  # 30 days including today
    end_date = today
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    print(f"Testing API with date range: {start_str} to {end_str}")
    
    try:
        # Call the API
        url = f"http://localhost:5000/api/dashboard-data?start={start_str}&end={end_str}"
        print(f"API URL: {url}")
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("\n=== API Response ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Extract the data we care about
            api_data = data.get('data', {})
            
            print("\n=== Key Values ===")
            print(f"periodSales: ฿{api_data.get('periodSales', 0):,.2f}")
            print(f"todaySales: ฿{api_data.get('todaySales', 0):,.2f}")
            print(f"weekSales: ฿{api_data.get('weekSales', 0):,.2f}")
            print(f"monthSales: ฿{api_data.get('monthSales', 0):,.2f}")
            print(f"totalCustomers: {api_data.get('totalCustomers', 0):,}")
            
            print("\n=== Expected vs Actual ===")
            print(f"Expected 30-day sales: ฿16,901.00")
            print(f"Actual periodSales: ฿{api_data.get('periodSales', 0):,.2f}")
            print(f"Expected 30-day customers: 145")
            print(f"Actual totalCustomers: {api_data.get('totalCustomers', 0):,}")
            
        else:
            print(f"API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_dashboard_api()