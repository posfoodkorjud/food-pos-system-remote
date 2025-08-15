#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import DatabaseManager
from datetime import date, timedelta

def test_sales_summary_logic():
    """Test the sales summary logic directly"""
    print("Testing sales summary logic directly...")
    
    # Initialize database
    db = DatabaseManager()
    
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    print(f"Today date: {today_str}")
    
    # Week range (7 days ago)
    week_start = (today - timedelta(days=6)).strftime('%Y-%m-%d')
    print(f"Week range: {week_start} to {today_str}")
    
    # Month range
    month_start = today.replace(day=1).strftime('%Y-%m-%d')
    print(f"Month range: {month_start} to {today_str}")
    
    # Get data from database
    print("\n=== Fetching orders ===")
    today_orders = db.get_orders_by_date_range(today_str, today_str)
    print(f"Today orders count: {len(today_orders)}")
    
    week_orders = db.get_orders_by_date_range(week_start, today_str)
    print(f"Week orders count: {len(week_orders)}")
    
    month_orders = db.get_orders_by_date_range(month_start, today_str)
    print(f"Month orders count: {len(month_orders)}")
    
    all_orders = db.get_orders_by_date_range('2020-01-01', today_str)
    print(f"All orders count: {len(all_orders)}")
    
    # Calculate sales
    print("\n=== Calculating sales ===")
    today_completed = [o for o in today_orders if o.get('status') == 'completed']
    today_total = sum(order.get('total_amount', 0) for order in today_completed)
    print(f"Today completed orders: {len(today_completed)}, total: {today_total}")
    
    week_completed = [o for o in week_orders if o.get('status') == 'completed']
    week_total = sum(order.get('total_amount', 0) for order in week_completed)
    print(f"Week completed orders: {len(week_completed)}, total: {week_total}")
    
    month_completed = [o for o in month_orders if o.get('status') == 'completed']
    month_total = sum(order.get('total_amount', 0) for order in month_completed)
    print(f"Month completed orders: {len(month_completed)}, total: {month_total}")
    
    all_completed = [o for o in all_orders if o.get('status') == 'completed']
    total_total = sum(order.get('total_amount', 0) for order in all_completed)
    print(f"All completed orders: {len(all_completed)}, total: {total_total}")
    
    # Show some sample orders
    print("\n=== Sample orders ===")
    if all_completed:
        print("First 3 completed orders:")
        for i, order in enumerate(all_completed[:3]):
            print(f"  Order {i+1}: ID={order.get('id')}, Status={order.get('status')}, Total={order.get('total_amount')}, Date={order.get('created_at')}")
    
    # Final result
    result = {
        'today': {'total': today_total, 'orders': len(today_completed)},
        'week': {'total': week_total, 'orders': len(week_completed)},
        'month': {'total': month_total, 'orders': len(month_completed)},
        'total': {'total': total_total, 'orders': len(all_completed)}
    }
    
    print("\n=== Final Result ===")
    print(f"Result: {result}")
    
    return result

if __name__ == '__main__':
    test_sales_summary_logic()