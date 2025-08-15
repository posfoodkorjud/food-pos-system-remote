#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_order_116():
    """ตรวจสอบ order 116 และ 117"""
    try:
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ตรวจสอบ order 116
        cursor.execute('''
            SELECT order_item_id, item_id, customer_request 
            FROM order_items 
            WHERE order_id = 116
        ''')
        
        rows = cursor.fetchall()
        
        print(f"Order 116 items ({len(rows)} รายการ):")
        for row in rows:
            print(f"  Item {row[0]}: item_id={row[1]}, customer_request=\"{row[2]}\"")
        
        # ตรวจสอบ order 117
        cursor.execute('''
            SELECT order_item_id, item_id, customer_request 
            FROM order_items 
            WHERE order_id = 117
        ''')
        
        rows = cursor.fetchall()
        
        print(f"\nOrder 117 items ({len(rows)} รายการ):")
        for row in rows:
            print(f"  Item {row[0]}: item_id={row[1]}, customer_request=\"{row[2]}\"")
        
        # ตรวจสอบ order 118
        cursor.execute('''
            SELECT order_item_id, item_id, customer_request 
            FROM order_items 
            WHERE order_id = 118
        ''')
        
        rows = cursor.fetchall()
        
        print(f"\nOrder 118 items ({len(rows)} รายการ):")
        for row in rows:
            print(f"  Item {row[0]}: item_id={row[1]}, customer_request=\"{row[2]}\"")
        
        # ตรวจสอบ order 89 (ล่าสุด)
        cursor.execute('''
            SELECT order_item_id, item_id, customer_request 
            FROM order_items 
            WHERE order_id = 89
        ''')
        
        rows = cursor.fetchall()
        
        print(f"\nOrder 89 items ({len(rows)} รายการ):")
        for row in rows:
            print(f"  Item {row[0]}: item_id={row[1]}, customer_request=\"{row[2]}\"")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_order_116()