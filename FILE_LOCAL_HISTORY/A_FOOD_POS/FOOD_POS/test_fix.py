import requests
import json
from datetime import datetime, timedelta

def test_fix():
    """Test the fix for 30 days dashboard issue"""
    
    print("=== Testing Fix for 30 Days Dashboard Issue ===")
    
    # Test the exact API call that should happen when user clicks "30 วันล่าสุด"
    today = datetime.now()
    start_date = today - timedelta(days=29)  # 30 days including today
    end_date = today
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    print(f"Testing 30 days range: {start_str} to {end_str}")
    
    try:
        url = f"http://localhost:5000/api/dashboard-data?start={start_str}&end={end_str}"
        print(f"API URL: {url}")
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            api_data = data.get('data', {})
            
            print("\n=== API Response for 30 Days ===")
            print(f"periodSales: ฿{api_data.get('periodSales', 0):,.2f}")
            print(f"totalCustomers: {api_data.get('totalCustomers', 0):,}")
            
            print("\n=== Expected Result ===")
            print("After the fix, when user clicks '30 วันล่าสุด' button:")
            print(f"- today-sales card should show: ฿{api_data.get('periodSales', 0):,.2f}")
            print(f"- total-customers card should show: {api_data.get('totalCustomers', 0):,} ลูกค้า")
            
            print("\n=== Before vs After Fix ===")
            print("Before fix:")
            print("  - today-sales card showed: ฿3,630 (wrong - was using 7 days data)")
            print("  - total-customers card showed: 17 ลูกค้า (wrong - was using 7 days data)")
            print("After fix:")
            print(f"  - today-sales card should show: ฿{api_data.get('periodSales', 0):,.2f} (correct - using 30 days data)")
            print(f"  - total-customers card should show: {api_data.get('totalCustomers', 0):,} ลูกค้า (correct - using 30 days data)")
            
            # Also test 7 days to make sure it still works
            print("\n=== Testing 7 Days (should still work) ===")
            week_start = (today - timedelta(days=6)).strftime('%Y-%m-%d')
            week_end = today.strftime('%Y-%m-%d')
            
            week_url = f"http://localhost:5000/api/dashboard-data?start={week_start}&end={week_end}"
            week_response = requests.get(week_url)
            
            if week_response.status_code == 200:
                week_data = week_response.json().get('data', {})
                print(f"7 days periodSales: ฿{week_data.get('periodSales', 0):,.2f}")
                print(f"7 days totalCustomers: {week_data.get('totalCustomers', 0):,}")
                print("✓ 7 days data looks correct")
            
        else:
            print(f"API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== Instructions ===")
    print("1. Open http://localhost:5000/frontend/admin.html")
    print("2. Click the '30 วันล่าสุด' button")
    print("3. Check if the today-sales card shows ฿15,318 and total-customers shows 104")
    print("4. If it shows the correct values, the fix is working!")

if __name__ == "__main__":
    test_fix()