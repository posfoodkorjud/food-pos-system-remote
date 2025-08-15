import sqlite3
import datetime

def check_30_days_sales():
    # Connect to database
    conn = sqlite3.connect('pos_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Calculate 30 days ago from today
        today = datetime.date.today()
        thirty_days_ago = today - datetime.timedelta(days=30)
        
        print(f"Checking sales for the last 30 days:")
        print(f"From: {thirty_days_ago} to: {today}")
        print("=" * 60)
        
        # Check completed orders in the last 30 days
        cursor.execute("""
            SELECT 
                COUNT(*) as order_count,
                COALESCE(SUM(total_amount), 0) as total_sales,
                DATE(completed_at) as sale_date
            FROM orders 
            WHERE status = 'completed' 
            AND DATE(completed_at) >= ?
            AND DATE(completed_at) <= ?
            GROUP BY DATE(completed_at)
            ORDER BY sale_date DESC
        """, (thirty_days_ago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')))
        
        daily_sales = cursor.fetchall()
        
        print(f"Daily sales breakdown ({len(daily_sales)} days with sales):")
        print("-" * 60)
        
        total_orders_30days = 0
        total_amount_30days = 0
        
        for day in daily_sales:
            print(f"{day['sale_date']}: {day['order_count']} orders, {day['total_sales']} บาท")
            total_orders_30days += day['order_count']
            total_amount_30days += day['total_sales']
        
        print("-" * 60)
        print(f"TOTAL FOR LAST 30 DAYS:")
        print(f"Orders: {total_orders_30days}")
        print(f"Amount: {total_amount_30days} บาท")
        
        # Also check what the API month endpoint returns
        print("\n" + "="*60)
        print("CHECKING API MONTH CALCULATION:")
        
        # Check current month sales (like the API does)
        current_month_start = today.replace(day=1)
        cursor.execute("""
            SELECT 
                COUNT(*) as order_count,
                COALESCE(SUM(total_amount), 0) as total_sales
            FROM orders 
            WHERE status = 'completed' 
            AND DATE(completed_at) >= ?
        """, (current_month_start.strftime('%Y-%m-%d'),))
        
        month_result = cursor.fetchone()
        print(f"Current month (from {current_month_start}): {month_result['order_count']} orders, {month_result['total_sales']} บาท")
        
        # Check if there are any active orders that might affect the calculation
        print("\n" + "="*60)
        print("CHECKING ACTIVE ORDERS (NOT COUNTED IN SALES):")
        
        cursor.execute("""
            SELECT 
                COUNT(*) as active_count,
                COALESCE(SUM(total_amount), 0) as active_total
            FROM orders 
            WHERE status != 'completed'
            AND status != 'rejected'
        """)
        
        active_result = cursor.fetchone()
        print(f"Active orders: {active_result['active_count']} orders, {active_result['active_total']} บาท")
        
        if active_result['active_count'] > 0:
            print("\nActive orders details:")
            cursor.execute("""
                SELECT order_id, table_id, status, total_amount, created_at
                FROM orders 
                WHERE status != 'completed'
                AND status != 'rejected'
                ORDER BY created_at DESC
            """)
            
            active_orders = cursor.fetchall()
            for order in active_orders:
                print(f"  Order {order['order_id']} (Table {order['table_id']}): {order['status']}, {order['total_amount']} บาท, {order['created_at']}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_30_days_sales()