#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to check Flask routes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app import app

def debug_routes():
    """Debug Flask routes"""
    print("Flask App Routes Debug")
    print("=" * 50)
    
    print(f"App name: {app.name}")
    print(f"App config: {app.config}")
    print(f"App debug: {app.debug}")
    print(f"App testing: {app.testing}")
    
    print("\nAll registered routes:")
    print("-" * 30)
    
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"{rule.rule:<60} {methods:<20} {rule.endpoint}")
    
    print("\nRoutes containing 'move':")
    print("-" * 30)
    
    move_routes = [rule for rule in app.url_map.iter_rules() if 'move' in rule.rule]
    if move_routes:
        for rule in move_routes:
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f"{rule.rule:<60} {methods:<20} {rule.endpoint}")
    else:
        print("No routes containing 'move' found!")
    
    print("\nRoutes containing 'categories':")
    print("-" * 30)
    
    category_routes = [rule for rule in app.url_map.iter_rules() if 'categories' in rule.rule]
    if category_routes:
        for rule in category_routes:
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f"{rule.rule:<60} {methods:<20} {rule.endpoint}")
    else:
        print("No routes containing 'categories' found!")

if __name__ == '__main__':
    debug_routes()