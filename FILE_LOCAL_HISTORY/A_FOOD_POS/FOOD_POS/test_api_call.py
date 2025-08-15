#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_sales_summary_api():
    """Test the sales summary API endpoint"""
    print("Testing sales summary API endpoint...")
    
    try:
        # Make API call
        response = requests.get('http://localhost:5000/api/sales-summary')
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data: {json.dumps(data, indent=2)}")
        else:
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Make sure Flask server is running on localhost:5000")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    test_sales_summary_api()