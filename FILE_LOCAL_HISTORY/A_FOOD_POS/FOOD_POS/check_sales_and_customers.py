import sqlite3
from datetime import datetime, timedelta
import os

def get_database_path():
    """Get the correct database path"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'pos_database.db')
    return db_path

def check_database_structure():
    """Check database structure to understand table schema"""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📋 ตารางในฐานข้อมูล:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check orders table structure
        if any('orders' in str(table) for table in tables):
            cursor.execute("PRAGMA table_info(orders);")
            columns = cursor.fetchall()
            
            print("\n📊 โครงสร้างตาราง orders:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        # Check if there are any records
        try:
            cursor.execute("SELECT COUNT(*) FROM orders;")
            count = cursor.fetchone()[0]
            print(f"\n📈 จำนวนรายการในตาราง orders: {count}")
            
            if count > 0:
                cursor.execute("SELECT * FROM orders LIMIT 3;")
                sample_data = cursor.fetchall()
                print("\n🔍 ตัวอย่างข้อมูล 3 รายการแรก:")
                for i, row in enumerate(sample_data, 1):
                    print(f"  {i}. {row}")
        except Exception as e:
            print(f"Error checking orders table: {e}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def check_sales_and_customers():
    """Check sales and customer count for current month and last 30 days"""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First check the structure
        check_database_structure()
        
        # Get current date
        now = datetime.now()
        
        # Calculate current month range (1st to last day of current month)
        month_start = datetime(now.year, now.month, 1)
        if now.month == 12:
            month_end = datetime(now.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(now.year, now.month + 1, 1) - timedelta(days=1)
        
        # Calculate last 30 days range
        days_30_start = now - timedelta(days=29)  # 30 days including today
        days_30_end = now
        
        print("\n" + "=" * 60)
        print("📊 รายงานยอดขายและจำนวนลูกค้า")
        print("=" * 60)
        
        # Try different possible column names for date
        date_columns = ['order_time', 'created_at', 'date', 'order_date', 'timestamp']
        amount_columns = ['total_amount', 'total', 'amount', 'price']
        
        # Get actual column names
        cursor.execute("PRAGMA table_info(orders);")
        columns_info = cursor.fetchall()
        actual_columns = [col[1] for col in columns_info]
        
        print(f"\n🔍 คอลัมน์ที่มีในตาราง: {actual_columns}")
        
        # Find the correct date and amount columns
        date_col = None
        amount_col = None
        
        for col in date_columns:
            if col in actual_columns:
                date_col = col
                break
        
        for col in amount_columns:
            if col in actual_columns:
                amount_col = col
                break
        
        if not date_col:
            print("❌ ไม่พบคอลัมน์วันที่ในตาราง")
            return
        
        if not amount_col:
            print("❌ ไม่พบคอลัมน์ยอดเงินในตาราง")
            return
        
        print(f"✅ ใช้คอลัมน์วันที่: {date_col}")
        print(f"✅ ใช้คอลัมน์ยอดเงิน: {amount_col}")
        
        # 1. Current month sales and customer count
        print(f"\n🗓️  ยอดขายเดือนนี้ ({month_start.strftime('%d/%m/%Y')} - {month_end.strftime('%d/%m/%Y')})")
        print("-" * 50)
        
        # Query for current month
        query = f"""
            SELECT 
                COUNT(*) as total_orders,
                SUM({amount_col}) as total_sales
            FROM orders 
            WHERE DATE({date_col}) >= DATE(?) 
            AND DATE({date_col}) <= DATE(?)
        """
        
        # Add status filter if status column exists
        if 'status' in actual_columns:
            query += " AND status != 'cancelled'"
        
        cursor.execute(query, (month_start.strftime('%Y-%m-%d'), month_end.strftime('%Y-%m-%d')))
        
        month_result = cursor.fetchone()
        month_orders = month_result[0] if month_result[0] else 0
        month_sales = month_result[1] if month_result[1] else 0
        
        print(f"💰 ยอดขาย: ฿{month_sales:,.2f}")
        print(f"👥 จำนวนลูกค้า (บิล): {month_orders:,} บิล")
        
        # 2. Last 30 days sales and customer count
        print(f"\n📅 ยอดขาย 30 วันล่าสุด ({days_30_start.strftime('%d/%m/%Y')} - {days_30_end.strftime('%d/%m/%Y')})")
        print("-" * 50)
        
        # Query for last 30 days
        cursor.execute(query, (days_30_start.strftime('%Y-%m-%d'), days_30_end.strftime('%Y-%m-%d')))
        
        days_30_result = cursor.fetchone()
        days_30_orders = days_30_result[0] if days_30_result[0] else 0
        days_30_sales = days_30_result[1] if days_30_result[1] else 0
        
        print(f"💰 ยอดขาย: ฿{days_30_sales:,.2f}")
        print(f"👥 จำนวนลูกค้า (บิล): {days_30_orders:,} บิล")
        
        print("\n" + "=" * 60)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_sales_and_customers()