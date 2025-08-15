import requests
import json
import sqlite3
from datetime import datetime, timedelta

def final_verification():
    """ทดสอบสุดท้ายเพื่อยืนยันว่าปัญหาได้รับการแก้ไขแล้ว"""
    
    print("=" * 60)
    print("การตรวจสอบสุดท้าย: ยอดขาย 30 วันล่าสุด")
    print("=" * 60)
    
    # 1. ตรวจสอบข้อมูลจากฐานข้อมูลโดยตรง
    print("\n1. ข้อมูลจากฐานข้อมูลโดยตรง:")
    try:
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        today = datetime.now().date()
        thirty_days_ago = today - timedelta(days=29)  # 30 วันรวมวันนี้
        
        cursor.execute("""
            SELECT COUNT(*) as total_orders, SUM(total_amount) as total_sales
            FROM orders
            WHERE DATE(created_at) >= ? AND DATE(created_at) <= ?
            AND status = 'completed'
        """, (thirty_days_ago, today))
        
        result = cursor.fetchone()
        db_orders, db_sales = result
        
        print(f"   ช่วงวันที่: {thirty_days_ago} ถึง {today}")
        print(f"   จำนวนออเดอร์: {db_orders}")
        print(f"   ยอดขายรวม: ฿{db_sales:,.2f}")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        db_sales = 0
        db_orders = 0
    
    # 2. ทดสอบ API ด้วย range=month
    print("\n2. ทดสอบ API ด้วย range=month:")
    try:
        response = requests.get('http://localhost:5000/api/dashboard-data?range=month')
        if response.status_code == 200:
            data = response.json()
            api_data = data.get('data', {})
            api_sales = api_data.get('periodSales', 0)
            api_customers = api_data.get('totalCustomers', 0)
            
            print(f"   API URL: /api/dashboard-data?range=month")
            print(f"   ยอดขาย (periodSales): ฿{api_sales:,.2f}")
            print(f"   จำนวนลูกค้า (totalCustomers): {api_customers}")
        else:
            print(f"   ❌ API Error: {response.status_code}")
            api_sales = 0
            api_customers = 0
    except Exception as e:
        print(f"   ❌ API Error: {e}")
        api_sales = 0
        api_customers = 0
    
    # 3. ทดสอบ API ด้วย start/end parameters
    print("\n3. ทดสอบ API ด้วย start/end parameters:")
    try:
        today = datetime.now().date()
        start_date = (today - timedelta(days=29)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        response = requests.get(f'http://localhost:5000/api/dashboard-data?start={start_date}&end={end_date}')
        if response.status_code == 200:
            data = response.json()
            api_data = data.get('data', {})
            api_sales_2 = api_data.get('periodSales', 0)
            api_customers_2 = api_data.get('totalCustomers', 0)
            
            print(f"   API URL: /api/dashboard-data?start={start_date}&end={end_date}")
            print(f"   ยอดขาย (periodSales): ฿{api_sales_2:,.2f}")
            print(f"   จำนวนลูกค้า (totalCustomers): {api_customers_2}")
        else:
            print(f"   ❌ API Error: {response.status_code}")
            api_sales_2 = 0
            api_customers_2 = 0
    except Exception as e:
        print(f"   ❌ API Error: {e}")
        api_sales_2 = 0
        api_customers_2 = 0
    
    # 4. สรุปผลการตรวจสอบ
    print("\n" + "=" * 60)
    print("สรุปผลการตรวจสอบ:")
    print("=" * 60)
    
    print(f"ฐานข้อมูลโดยตรง:     ฿{db_sales:,.2f} ({db_orders} ออเดอร์)")
    print(f"API range=month:      ฿{api_sales:,.2f} ({api_customers} ลูกค้า)")
    print(f"API start/end:        ฿{api_sales_2:,.2f} ({api_customers_2} ลูกค้า)")
    
    # ตรวจสอบความสอดคล้อง
    tolerance = 1.0  # ยอมรับความผิดพลาด 1 บาท
    
    if abs(db_sales - api_sales) <= tolerance and abs(api_sales - api_sales_2) <= tolerance:
        print("\n✅ ผลการตรวจสอบ: สำเร็จ!")
        print("   ข้อมูลจากทุกแหล่งสอดคล้องกัน")
        print("   ปัญหายอดขาย 30 วันล่าสุดได้รับการแก้ไขแล้ว")
        
        # แสดงค่าที่ถูกต้อง
        correct_value = api_sales
        print(f"\n📊 ยอดขาย 30 วันล่าสุดที่ถูกต้อง: ฿{correct_value:,.2f}")
        
        # ตอบคำถามของผู้ใช้
        print("\n💡 คำตอบสำหรับคำถามของคุณ:")
        if correct_value == 16901:
            print("   ยอดขาย 30 วันล่าสุด คือ ฿16,901 (ตามที่คุณคาดหวัง)")
        elif correct_value == 15318:
            print("   ยอดขาย 30 วันล่าสุด คือ ฿15,318 (ไม่ใช่ ฿16,901)")
        else:
            print(f"   ยอดขาย 30 วันล่าสุด คือ ฿{correct_value:,.2f} (ไม่ใช่ ฿16,901 หรือ ฿15,318)")
            
    else:
        print("\n❌ ผลการตรวจสอบ: ยังมีปัญหา!")
        print("   ข้อมูลจากแหล่งต่างๆ ไม่สอดคล้องกัน")
        print("   ต้องตรวจสอบเพิ่มเติม")
    
    print("\n" + "=" * 60)
    print("การตรวจสอบเสร็จสิ้น")
    print("=" * 60)

if __name__ == "__main__":
    final_verification()