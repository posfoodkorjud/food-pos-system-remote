#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare Flask app instances
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app import app

print("=== Flask App Instance Analysis ===")
print(f"App name: {app.name}")
print(f"App debug: {app.debug}")
print(f"App config: {dict(app.config)}")
print(f"App instance: {app}")
print(f"App blueprints: {list(app.blueprints.keys())}")

print("\n=== Registered Routes ===")
for rule in app.url_map.iter_rules():
    methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    print(f"{rule.rule:<50} {methods}")

print("\n=== Move Routes Only ===")
for rule in app.url_map.iter_rules():
    if 'move' in rule.rule:
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"{rule.rule:<50} {methods}")

print("\n=== Testing Flask Test Client ===")
with app.test_client() as client:
    # Test GET categories
    response = client.get('/api/menu/categories')
    print(f"GET /api/menu/categories: {response.status_code}")
    
    # Test POST move-down
    response = client.post('/api/menu/categories/2/move-down')
    print(f"POST /api/menu/categories/2/move-down: {response.status_code}")
    print(f"Response: {response.get_data(as_text=True)}")