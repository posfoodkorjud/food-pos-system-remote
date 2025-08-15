#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

def check_orders():
    """ตรวจสอบข้อมูลออเดอร์ในฐานข้อมูล"""
    
    # เชื่อมต่อฐานข้อมูล
    conn = sqlite3.connect('pos_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=== ตรวจสอบข้อมูลออเดอร์ ===")
    
    # ตรวจสอบจำนวนออเดอร์ทั้งหมด
    cursor.execute("SELECT COUNT(*) as total FROM orders")
    total_orders = cursor.fetchone()['total']
    print(f"จำนวนออเดอร์ทั้งหมด: {total_orders}")
    
    # ตรวจสอบออเดอร์ล่าสุด 10 รายการ
    print("\n=== ออเดอร์ล่าสุด 10 รายการ ===")
    cursor.execute("""
        SELECT o.order_id, o.table_id, t.table_name, o.status, o.total_amount, 
               o.created_at, o.completed_at
        FROM orders o
        LEFT JOIN tables t ON o.table_id = t.table_id
        ORDER BY o.created_at DESC
        LIMIT 10
    """)
    
    orders = cursor.fetchall()
    for order in orders:
        print(f"Order ID: {order['order_id']}, โต๊ะ: {order['table_name']}, "
              f"สถานะ: {order['status']}, ยอดรวม: {order['total_amount']} บาท, "
              f"สั่งเมื่อ: {order['created_at']}")
    
    # ตรวจสอบรายการอาหารในออเดอร์ล่าสุด
    if orders:
        latest_order_id = orders[0]['order_id']
        print(f"\n=== รายการอาหารในออเดอร์ {latest_order_id} ===")
        
        cursor.execute("""
            SELECT oi.order_item_id, oi.quantity, oi.unit_price, oi.total_price,
                   oi.status, oi.customer_request, mi.name as item_name
            FROM order_items oi
            LEFT JOIN menu_items mi ON oi.item_id = mi.item_id
            WHERE oi.order_id = ?
            ORDER BY oi.order_item_id
        """, (latest_order_id,))
        
        order_items = cursor.fetchall()
        for item in order_items:
            print(f"- {item['item_name']} x{item['quantity']} = {item['total_price']} บาท "
                  f"(สถานะ: {item['status']})")
            if item['customer_request']:
                print(f"  หมายเหตุ: {item['customer_request']}")
    
    # สถิติออเดอร์ตามสถานะ
    print("\n=== สถิติออเดอร์ตามสถานะ ===")
    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM orders
        GROUP BY status
        ORDER BY count DESC
    """)
    
    status_stats = cursor.fetchall()
    for stat in status_stats:
        print(f"สถานะ '{stat['status']}': {stat['count']} ออเดอร์")
    
    # สถิติรายการอาหารตามสถานะ
    print("\n=== สถิติรายการอาหารตามสถานะ ===")
    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM order_items
        GROUP BY status
        ORDER BY count DESC
    """)
    
    item_status_stats = cursor.fetchall()
    for stat in item_status_stats:
        print(f"สถานะ '{stat['status']}': {stat['count']} รายการ")
    
    # อาหารที่ขายดีที่สุด
    print("\n=== อาหารที่ขายดีที่สุด 10 อันดับ ===")
    cursor.execute("""
        SELECT mi.name, SUM(oi.quantity) as total_sold, 
               SUM(oi.total_price) as total_revenue
        FROM order_items oi
        LEFT JOIN menu_items mi ON oi.item_id = mi.item_id
        GROUP BY oi.item_id, mi.name
        ORDER BY total_sold DESC
        LIMIT 10
    """)
    
    popular_items = cursor.fetchall()
    for i, item in enumerate(popular_items, 1):
        print(f"{i}. {item['name']}: ขายได้ {item['total_sold']} จาน, "
              f"รายได้ {item['total_revenue']} บาท")
    
    conn.close()
    print("\n=== เสร็จสิ้นการตรวจสอบออเดอร์ ===")

if __name__ == "__main__":
    check_orders()