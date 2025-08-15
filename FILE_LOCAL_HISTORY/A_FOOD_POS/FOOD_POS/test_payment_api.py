#!/usr/bin/env python3
import requests
import json

def test_payment_complete():
    """Test the payment-complete API endpoint"""
    # First test a known working endpoint
    print("=== Testing GET /api/orders (should work) ===")
    try:
        response = requests.get("http://localhost:5001/api/orders", timeout=5)
        print(f"GET /api/orders - Status: {response.status_code}")
    except Exception as e:
        print(f"GET /api/orders failed: {e}")
    
    print("\n=== Testing POST /api/tables/8/payment-complete ===")
    url = "http://localhost:5001/api/tables/8/payment-complete"
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Testing POST {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.post(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                json_data = response.json()
                print(f"JSON Response: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print("Failed to decode JSON response")
                
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_payment_complete()