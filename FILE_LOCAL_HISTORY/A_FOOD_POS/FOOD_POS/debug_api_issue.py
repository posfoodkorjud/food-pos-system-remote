import requests
import json
from datetime import datetime, timedelta

def test_api_endpoints():
    base_url = "http://localhost:5000"
    
    print("ทดสอบ API endpoints ต่างๆ:")
    print("="*50)
    
    # Test different range parameters
    ranges = ['today', 'week', 'month']
    
    for range_param in ranges:
        try:
            url = f"{base_url}/api/dashboard-data?range={range_param}"
            print(f"\nทดสอบ URL: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print(f"Error Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"ไม่สามารถเชื่อมต่อกับ {url}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Test without range parameter
    try:
        url = f"{base_url}/api/dashboard-data"
        print(f"\nทดสอบ URL (ไม่มี range): {url}")
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test if backend is running
    try:
        url = f"{base_url}/"
        print(f"\nทดสอบ Backend Root: {url}")
        response = requests.get(url, timeout=5)
        print(f"Backend Status: {response.status_code}")
    except Exception as e:
        print(f"Backend ไม่ทำงาน: {e}")

if __name__ == "__main__":
    test_api_endpoints()