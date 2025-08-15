import sqlite3
import datetime

def check_today_orders():
    # Connect to database
    conn = sqlite3.connect('pos_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get today's date
    today = datetime.date.today().strftime('%Y-%m-%d')
    print(f"Checking orders for today: {today}")
    
    try:
        # Check all orders for today
        cursor.execute("""
            SELECT order_id, table_id, status, total_amount, created_at, completed_at, bill_status
            FROM orders 
            WHERE DATE(created_at) = ?
            ORDER BY created_at DESC
        """, (today,))
        
        orders = cursor.fetchall()
        print(f"\nFound {len(orders)} orders for today:")
        
        total_today = 0
        completed_orders = 0
        
        for order in orders:
            print(f"\nOrder ID: {order['order_id']}")
            print(f"Table: {order['table_id']}")
            print(f"Status: {order['status']}")
            print(f"Total: {order['total_amount']} บาท")
            print(f"Created: {order['created_at']}")
            print(f"Completed: {order['completed_at']}")
            print(f"Bill Status: {order['bill_status']}")
            
            # Count completed orders and their totals
            if order['status'] == 'completed':
                completed_orders += 1
                total_today += order['total_amount']
                
                # Get order items for this order
                cursor.execute("""
                    SELECT oi.*, mi.name as item_name, mi.price as item_price
                    FROM order_items oi
                    JOIN menu_items mi ON oi.item_id = mi.item_id
                    WHERE oi.order_id = ?
                """, (order['order_id'],))
                
                items = cursor.fetchall()
                print(f"  Items ({len(items)}):")
                for item in items:
                    print(f"    - {item['item_name']}: {item['quantity']}x {item['item_price']} = {item['quantity'] * item['item_price']} บาท")
            
            print("-" * 50)
        
        print(f"\nSUMMARY FOR TODAY ({today}):")
        print(f"Total orders: {len(orders)}")
        print(f"Completed orders: {completed_orders}")
        print(f"Total sales from completed orders: {total_today} บาท")
        
        # Also check what the API returns
        print("\n" + "="*60)
        print("CHECKING API SALES SUMMARY:")
        
        # Check sales summary like the API does
        cursor.execute("""
            SELECT 
                COUNT(*) as order_count,
                COALESCE(SUM(total_amount), 0) as total_sales
            FROM orders 
            WHERE status = 'completed' 
            AND DATE(completed_at) = ?
        """, (today,))
        
        api_result = cursor.fetchone()
        print(f"API would return - Today: {api_result['order_count']} orders, {api_result['total_sales']} บาท")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_today_orders()