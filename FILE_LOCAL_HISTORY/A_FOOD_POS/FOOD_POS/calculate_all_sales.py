#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

def calculate_sales_all_status():
    """คำนวณยอดขายโดยรวมทุกสถานะยกเว้น 'rejected'"""
    
    # เชื่อมต่อฐานข้อมูล
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    try:
        # ดึงข้อมูลออเดอร์ทั้งหมดที่ไม่ใช่ 'rejected'
        query = """
        SELECT 
            status,
            COUNT(*) as order_count,
            SUM(total_amount) as total_amount
        FROM orders 
        WHERE status != 'rejected'
        GROUP BY status
        ORDER BY status
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print("=== สรุปยอดขายตามสถานะ (ยกเว้น 'rejected') ===")
        print(f"{'สถานะ':<15} {'จำนวนออเดอร์':<15} {'ยอดรวม (บาท)':<20}")
        print("-" * 50)
        
        total_orders = 0
        total_sales = 0
        
        for status, count, amount in results:
            print(f"{status:<15} {count:<15} {amount:,.2f}")
            total_orders += count
            total_sales += amount if amount else 0
        
        print("-" * 50)
        print(f"{'รวมทั้งหมด':<15} {total_orders:<15} {total_sales:,.2f}")
        
        # ดึงข้อมูลรายวัน (วันนี้)
        today = datetime.now().strftime('%Y-%m-%d')
        
        query_today = """
        SELECT 
            status,
            COUNT(*) as order_count,
            SUM(total_amount) as total_amount
        FROM orders 
        WHERE DATE(created_at) = ? AND status != 'rejected'
        GROUP BY status
        ORDER BY status
        """
        
        cursor.execute(query_today, (today,))
        today_results = cursor.fetchall()
        
        print(f"\n=== ยอดขายวันนี้ ({today}) ====")
        print(f"{'สถานะ':<15} {'จำนวนออเดอร์':<15} {'ยอดรวม (บาท)':<20}")
        print("-" * 50)
        
        today_total_orders = 0
        today_total_sales = 0
        
        for status, count, amount in today_results:
            print(f"{status:<15} {count:<15} {amount:,.2f}")
            today_total_orders += count
            today_total_sales += amount if amount else 0
        
        print("-" * 50)
        print(f"{'รวมทั้งหมด':<15} {today_total_orders:<15} {today_total_sales:,.2f}")
        
        # เปรียบเทียบกับยอดขาย 'completed' เท่านั้น
        query_completed_only = """
        SELECT 
            COUNT(*) as order_count,
            SUM(total_amount) as total_amount
        FROM orders 
        WHERE DATE(created_at) = ? AND status = 'completed'
        """
        
        cursor.execute(query_completed_only, (today,))
        completed_result = cursor.fetchone()
        
        completed_orders = completed_result[0] if completed_result[0] else 0
        completed_sales = completed_result[1] if completed_result[1] else 0
        
        print(f"\n=== เปรียบเทียบ ====")
        print(f"ยอดขายเฉพาะ 'completed': {completed_orders} ออเดอร์, {completed_sales:,.2f} บาท")
        print(f"ยอดขายรวมทุกสถานะ (ยกเว้น 'rejected'): {today_total_orders} ออเดอร์, {today_total_sales:,.2f} บาท")
        print(f"ส่วนต่าง: {today_total_orders - completed_orders} ออเดอร์, {today_total_sales - completed_sales:,.2f} บาท")
        
        return {
            'total_all_status': {
                'orders': today_total_orders,
                'sales': today_total_sales
            },
            'completed_only': {
                'orders': completed_orders,
                'sales': completed_sales
            },
            'difference': {
                'orders': today_total_orders - completed_orders,
                'sales': today_total_sales - completed_sales
            }
        }
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        return None
    
    finally:
        conn.close()

if __name__ == "__main__":
    result = calculate_sales_all_status()
    
    if result:
        print(f"\n=== สรุปผลลัพธ์ ====")
        print(f"ระบบแอดมิน (รวมทุกสถานะยกเว้น 'rejected'): {result['total_all_status']['sales']:,.2f} บาท")
        print(f"Google Sheets (เฉพาะ 'completed'): {result['completed_only']['sales']:,.2f} บาท")
        print(f"ความแตกต่าง: {result['difference']['sales']:,.2f} บาท")