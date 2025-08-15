import requests
import json
import sqlite3
from datetime import datetime, timedelta

def explain_sales_discrepancy():
    """อธิบายความแตกต่างระหว่างยอดขายที่แสดงในฐานข้อมูลและ API"""
    
    print("=" * 80)
    print("การอธิบายความแตกต่างของยอดขาย 30 วันล่าสุด")
    print("=" * 80)
    
    # คำนวณช่วงวันที่ 30 วัน
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=29)  # 30 วันรวมวันนี้
    
    print(f"\nช่วงวันที่ที่ใช้: {thirty_days_ago} ถึง {today}")
    
    # 1. ตรวจสอบข้อมูลจากฐานข้อมูลโดยตรง (SQL แบบง่าย)
    print("\n" + "="*50)
    print("1. ข้อมูลจากฐานข้อมูลโดยตรง (SQL แบบง่าย)")
    print("="*50)
    
    try:
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # SQL Query แบบง่าย
        cursor.execute("""
            SELECT COUNT(*) as total_orders, SUM(total_amount) as total_sales
            FROM orders
            WHERE DATE(created_at) >= ? AND DATE(created_at) <= ?
            AND status != 'rejected'
        """, (thirty_days_ago, today))
        
        result = cursor.fetchone()
        simple_orders, simple_sales = result
        
        print(f"   SQL Query: SELECT COUNT(*), SUM(total_amount) FROM orders")
        print(f"   WHERE DATE(created_at) BETWEEN '{thirty_days_ago}' AND '{today}'")
        print(f"   AND status != 'rejected'")
        print(f"   ผลลัพธ์: {simple_orders} ออเดอร์, ฿{simple_sales:,.2f}")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        simple_sales = 0
        simple_orders = 0
    
    # 2. ตรวจสอบข้อมูลจาก get_orders_by_date_range (ที่ API ใช้)
    print("\n" + "="*50)
    print("2. ข้อมูลจาก get_orders_by_date_range (ที่ API ใช้)")
    print("="*50)
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from database import DatabaseManager
        
        db = DatabaseManager()
        start_str = thirty_days_ago.strftime('%Y-%m-%d')
        end_str = today.strftime('%Y-%m-%d')
        
        orders = db.get_orders_by_date_range(start_str, end_str)
        
        print(f"   ฟังก์ชัน: db.get_orders_by_date_range('{start_str}', '{end_str}')")
        print(f"   จำนวนออเดอร์ที่ได้: {len(orders)}")
        
        # คำนวณยอดขายแบบเดียวกับ API
        api_style_sales = 0
        api_style_customers = 0
        
        for order in orders:
            if order.get('status') != 'rejected':
                api_style_sales += order.get('total_amount', 0)
                api_style_customers += 1
        
        print(f"   ยอดขายรวม (API style): ฿{api_style_sales:,.2f}")
        print(f"   จำนวนลูกค้า (API style): {api_style_customers}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        api_style_sales = 0
        api_style_customers = 0
    
    # 3. ทดสอบ API จริง
    print("\n" + "="*50)
    print("3. ข้อมูลจาก API จริง")
    print("="*50)
    
    try:
        response = requests.get('http://localhost:5000/api/dashboard-data?range=month')
        if response.status_code == 200:
            data = response.json()
            api_data = data.get('data', {})
            real_api_sales = api_data.get('periodSales', 0)
            real_api_customers = api_data.get('totalCustomers', 0)
            
            print(f"   API URL: /api/dashboard-data?range=month")
            print(f"   ยอดขาย (periodSales): ฿{real_api_sales:,.2f}")
            print(f"   จำนวนลูกค้า (totalCustomers): {real_api_customers}")
        else:
            print(f"   ❌ API Error: {response.status_code}")
            real_api_sales = 0
            real_api_customers = 0
    except Exception as e:
        print(f"   ❌ API Error: {e}")
        real_api_sales = 0
        real_api_customers = 0
    
    # 4. วิเคราะห์ความแตกต่าง
    print("\n" + "="*80)
    print("4. การวิเคราะห์ความแตกต่าง")
    print("="*80)
    
    print(f"\nสรุปผลลัพธ์:")
    print(f"   SQL โดยตรง:           ฿{simple_sales:,.2f} ({simple_orders} ออเดอร์)")
    print(f"   get_orders_by_date_range: ฿{api_style_sales:,.2f} ({api_style_customers} ลูกค้า)")
    print(f"   API จริง:              ฿{real_api_sales:,.2f} ({real_api_customers} ลูกค้า)")
    
    # ตรวจสอบความสอดคล้อง
    print("\n💡 การวิเคราะห์:")
    
    if abs(api_style_sales - real_api_sales) <= 1.0:
        print("   ✅ API และ get_orders_by_date_range สอดคล้องกัน")
    else:
        print("   ❌ API และ get_orders_by_date_range ไม่สอดคล้องกัน")
    
    if abs(simple_sales - api_style_sales) > 1.0:
        print("   ⚠️  SQL โดยตรงและ get_orders_by_date_range ให้ผลต่างกัน")
        print("       สาเหตุที่เป็นไปได้:")
        print("       - get_orders_by_date_range อาจมีการ JOIN ตารางเพิ่มเติม")
        print("       - อาจมีการกรองข้อมูลที่แตกต่างกัน")
        print("       - อาจมีปัญหาเรื่อง timezone หรือการแปลงวันที่")
    else:
        print("   ✅ SQL โดยตรงและ get_orders_by_date_range สอดคล้องกัน")
    
    # 5. คำตอบสำหรับคำถามของผู้ใช้
    print("\n" + "="*80)
    print("5. คำตอบสำหรับคำถาม: ยอดขาย 30 วันล่าสุด คือ ฿16,901 หรือ ฿15,318?")
    print("="*80)
    
    correct_value = real_api_sales if real_api_sales > 0 else api_style_sales
    
    print(f"\n📊 ยอดขาย 30 วันล่าสุดที่ถูกต้องตามระบบปัจจุบัน: ฿{correct_value:,.2f}")
    
    if abs(correct_value - 16901) < abs(correct_value - 15318):
        print("\n✅ ใกล้เคียงกับ ฿16,901 มากกว่า")
        print("   อาจเป็นเพราะ:")
        print("   - ข้อมูลในฐานข้อมูลมีการเปลี่ยนแปลงตั้งแต่ครั้งที่แล้ว")
        print("   - มีการเพิ่มหรือลบออเดอร์")
        print("   - มีการเปลี่ยนสถานะของออเดอร์")
    elif abs(correct_value - 15318) < abs(correct_value - 16901):
        print("\n✅ ใกล้เคียงกับ ฿15,318 มากกว่า")
        print("   นี่คือค่าที่ถูกต้องตามข้อมูลปัจจุบัน")
    else:
        print(f"\n⚠️  ค่าปัจจุบัน (฿{correct_value:,.2f}) ไม่ตรงกับทั้ง ฿16,901 และ ฿15,318")
        print("   อาจมีการเปลี่ยนแปลงข้อมูลในฐานข้อมูล")
    
    print("\n🔍 เหตุผลที่ค่าอาจแตกต่างจากที่คาดหวัง:")
    print("   1. ข้อมูลในฐานข้อมูลมีการเปลี่ยนแปลงตลอดเวลา")
    print("   2. การคำนวณช่วงวันที่อาจแตกต่างกัน (รวมวันนี้หรือไม่)")
    print("   3. การกรองสถานะออเดอร์ (rejected, completed, etc.)")
    print("   4. ปัญหาเรื่อง timezone หรือการแปลงวันที่")
    
    print("\n" + "="*80)
    print("การตรวจสอบเสร็จสิ้น")
    print("="*80)

if __name__ == "__main__":
    explain_sales_discrepancy()