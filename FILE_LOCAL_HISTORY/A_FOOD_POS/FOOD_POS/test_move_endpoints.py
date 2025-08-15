#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for move-up and move-down endpoints
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app import app
from backend.database import DatabaseManager

def test_endpoints():
    """Test move-up and move-down endpoints directly"""
    
    # Create test client
    with app.test_client() as client:
        print("Testing move-up and move-down endpoints...")
        print("=" * 50)
        
        # Test GET categories first
        print("1. Testing GET /api/menu/categories")
        response = client.get('/api/menu/categories')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            categories = response.get_json()
            print(f"   Found {len(categories)} categories")
            for cat in categories:
                print(f"   - ID: {cat['category_id']}, Name: {cat['name']}, Sort: {cat['sort_order']}")
        else:
            print(f"   Error: {response.get_data(as_text=True)}")
            return
        
        print("\n2. Testing POST /api/menu/categories/2/move-down")
        response = client.post('/api/menu/categories/2/move-down', 
                             headers={'Content-Type': 'application/json'})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_data(as_text=True)}")
        
        print("\n3. Testing POST /api/menu/categories/1/move-up")
        response = client.post('/api/menu/categories/1/move-up', 
                             headers={'Content-Type': 'application/json'})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_data(as_text=True)}")
        
        print("\n4. Testing all registered routes containing 'move'")
        for rule in app.url_map.iter_rules():
            if 'move' in rule.rule:
                methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
                print(f"   {rule.rule:<50} {methods}")

if __name__ == '__main__':
    test_endpoints()