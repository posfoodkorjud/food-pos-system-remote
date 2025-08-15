#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Flask server directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app import app

if __name__ == '__main__':
    print("Starting Flask server directly...")
    print("Available routes:")
    
    for rule in app.url_map.iter_rules():
        if 'move' in rule.rule:
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f"  {rule.rule:<50} {methods}")
    
    print("\nStarting server on http://localhost:5001")
    app.run(host='localhost', port=5001, debug=True)