import requests
import json

# ทดสอบเรียก API โดยตรง
url = "http://localhost:5000/api/tables/1/orders"
print(f"Testing API: {url}")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Raw Response: {response.text}")
    
    if response.headers.get('content-type', '').startswith('application/json'):
        data = response.json()
        print(f"JSON Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print("Response is not JSON")
        
except Exception as e:
    print(f"Error: {e}")