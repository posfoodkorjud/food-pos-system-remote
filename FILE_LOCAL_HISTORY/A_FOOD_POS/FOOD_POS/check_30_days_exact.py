import sqlite3
from datetime import datetime, timedelta

def check_30_days_sales():
    # Connect to database
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    # First, check table structure
    print("ตรวจสอบโครงสร้างตาราง:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"ตารางในฐานข้อมูล: {[table[0] for table in tables]}")
    
    # Check orders table structure
    cursor.execute("PRAGMA table_info(orders);")
    orders_columns = cursor.fetchall()
    print(f"\nคอลัมน์ในตาราง orders: {[col[1] for col in orders_columns]}")
    
    # Check order_items table structure if exists
    try:
        cursor.execute("PRAGMA table_info(order_items);")
        order_items_columns = cursor.fetchall()
        print(f"คอลัมน์ในตาราง order_items: {[col[1] for col in order_items_columns]}")
    except:
        print("ไม่มีตาราง order_items")
    
    # Calculate 30 days ago from today
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    print(f"\nวันนี้: {today}")
    print(f"30 วันที่แล้ว: {thirty_days_ago}")
    print("="*50)
    
    # Try different query based on actual table structure
    try:
        # First try to see what's in orders table
        cursor.execute("SELECT * FROM orders LIMIT 5;")
        sample_orders = cursor.fetchall()
        print(f"ตัวอย่างข้อมูลในตาราง orders: {sample_orders}")
        
        # Simple query for orders in 30 days
        simple_query = """
        SELECT COUNT(*) as total_orders,
               SUM(total_amount) as total_sales
        FROM orders
        WHERE DATE(created_at) >= ? AND DATE(created_at) <= ?
        AND status = 'completed'
        """
        
        cursor.execute(simple_query, (thirty_days_ago, today))
        result = cursor.fetchone()
        
        total_orders, total_sales = result
        print(f"\nจำนวนออเดอร์ทั้งหมด: {total_orders}")
        print(f"ยอดขายรวม 30 วัน: ฿{total_sales:,.2f}")
        
    except Exception as e:
        print(f"Error in query: {e}")
        
        # Try even simpler query
        try:
            cursor.execute("SELECT COUNT(*), SUM(total_amount) FROM orders WHERE status = 'completed'")
            result = cursor.fetchone()
            print(f"ออเดอร์ทั้งหมดที่เสร็จสิ้น: {result[0]}, ยอดรวม: ฿{result[1]:,.2f}")
        except Exception as e2:
            print(f"Error in simple query: {e2}")
    
    # Also check what the API endpoint returns
    print("\n" + "="*50)
    print("ตรวจสอบข้อมูลที่ API ส่งกลับ:")
    
    # Simulate API call logic
    import requests
    try:
        response = requests.get('http://localhost:5000/api/dashboard-data?range=month')
        if response.status_code == 200:
            data = response.json()
            print(f"API ส่งกลับ - ยอดขาย: ฿{data.get('periodSales', 0):,.2f}")
            print(f"API ส่งกลับ - ลูกค้า: {data.get('totalCustomers', 0)}")
        else:
            print(f"API Error: {response.status_code}")
    except Exception as e:
        print(f"ไม่สามารถเชื่อมต่อ API: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_30_days_sales()