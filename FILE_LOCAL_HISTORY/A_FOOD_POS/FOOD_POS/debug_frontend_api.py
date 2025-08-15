import requests
import json
from datetime import datetime, timedelta

def debug_frontend_api_calls():
    """Debug the exact API calls that frontend makes"""
    
    print("=== Debugging Frontend API Calls ===")
    
    # Test different scenarios that frontend might call
    scenarios = [
        {
            'name': 'Today (selectedDateRange = today)',
            'start': datetime.now().strftime('%Y-%m-%d'),
            'end': datetime.now().strftime('%Y-%m-%d')
        },
        {
            'name': '7 Days (selectedDateRange = week)',
            'start': (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'),
            'end': datetime.now().strftime('%Y-%m-%d')
        },
        {
            'name': '30 Days (selectedDateRange = month)',
            'start': (datetime.now() - timedelta(days=29)).strftime('%Y-%m-%d'),
            'end': datetime.now().strftime('%Y-%m-%d')
        },
        {
            'name': 'Chart Period 7 days (currentChartPeriod = 7)',
            'start': (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'),
            'end': datetime.now().strftime('%Y-%m-%d')
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        print(f"Date range: {scenario['start']} to {scenario['end']}")
        
        try:
            url = f"http://localhost:5000/api/dashboard-data?start={scenario['start']}&end={scenario['end']}"
            print(f"API URL: {url}")
            
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                api_data = data.get('data', {})
                
                print(f"✓ API Response:")
                print(f"  periodSales: ฿{api_data.get('periodSales', 0):,.2f}")
                print(f"  todaySales: ฿{api_data.get('todaySales', 0):,.2f}")
                print(f"  weekSales: ฿{api_data.get('weekSales', 0):,.2f}")
                print(f"  monthSales: ฿{api_data.get('monthSales', 0):,.2f}")
                print(f"  totalCustomers: {api_data.get('totalCustomers', 0):,}")
                
                # Check if this matches what we see on dashboard
                if scenario['name'] == '30 Days (selectedDateRange = month)':
                    print(f"\n🔍 ANALYSIS for 30 Days scenario:")
                    print(f"  Expected on dashboard: ฿3,630 and 17 customers")
                    print(f"  API returns: ฿{api_data.get('periodSales', 0):,.2f} and {api_data.get('totalCustomers', 0):,} customers")
                    
                    if api_data.get('periodSales', 0) != 3630:
                        print(f"  ❌ MISMATCH! API periodSales ({api_data.get('periodSales', 0)}) != Dashboard display (3630)")
                    else:
                        print(f"  ✅ Match! API and dashboard show same values")
                        
            else:
                print(f"❌ API Error: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n=== Summary ===")
    print("If API returns different values than dashboard shows, the issue is in frontend JavaScript.")
    print("If API returns same values as dashboard, the issue might be in backend calculation.")

if __name__ == "__main__":
    debug_frontend_api_calls()