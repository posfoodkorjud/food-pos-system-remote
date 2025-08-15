import sqlite3
import datetime

def check_active_orders():
    # Connect to database
    conn = sqlite3.connect('pos_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Check all active orders (not completed)
        cursor.execute("""
            SELECT order_id, table_id, session_id, status, total_amount, created_at, updated_at, bill_status
            FROM orders 
            WHERE status != 'completed'
            ORDER BY created_at DESC
        """)
        
        orders = cursor.fetchall()
        print(f"Found {len(orders)} active (non-completed) orders:")
        
        for order in orders:
            print(f"\nOrder ID: {order['order_id']}")
            print(f"Table: {order['table_id']}")
            print(f"Session ID: {order['session_id']}")
            print(f"Status: {order['status']}")
            print(f"Total: {order['total_amount']} บาท")
            print(f"Created: {order['created_at']}")
            print(f"Updated: {order['updated_at']}")
            print(f"Bill Status: {order['bill_status']}")
            
            # Get order items for this order
            try:
                cursor.execute("""
                    SELECT oi.*, mi.name as item_name, mi.price as item_price
                    FROM order_items oi
                    JOIN menu_items mi ON oi.item_id = mi.item_id
                    WHERE oi.order_id = ?
                """, (order['order_id'],))
                
                items = cursor.fetchall()
                print(f"  Items ({len(items)}):")
                item_total = 0
                for item in items:
                    item_subtotal = item['quantity'] * item['item_price']
                    item_total += item_subtotal
                    print(f"    - {item['item_name']}: {item['quantity']}x {item['item_price']} = {item_subtotal} บาท")
                    
                    # Check if there are any special options
                    if 'customer_request' in item.keys() and item['customer_request']:
                        print(f"      Special request: {item['customer_request']}")
                
                print(f"  Calculated total from items: {item_total} บาท")
                if item_total != order['total_amount']:
                    print(f"  ⚠️  MISMATCH: Order total ({order['total_amount']}) != Items total ({item_total})")
                    
            except Exception as e:
                print(f"  Error getting items: {e}")
            
            print("-" * 60)
        
        # Also check specifically for table 3
        print("\n" + "="*60)
        print("CHECKING SPECIFICALLY FOR TABLE 3:")
        
        cursor.execute("""
            SELECT order_id, table_id, session_id, status, total_amount, created_at, updated_at, bill_status
            FROM orders 
            WHERE table_id = 3
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        table3_orders = cursor.fetchall()
        print(f"Found {len(table3_orders)} recent orders for table 3:")
        
        for order in table3_orders:
            print(f"\nOrder ID: {order['order_id']}")
            print(f"Status: {order['status']}")
            print(f"Total: {order['total_amount']} บาท")
            print(f"Created: {order['created_at']}")
            print(f"Session ID: {order['session_id']}")
            
            # Check if this matches the amount from the image (1126 baht)
            if abs(order['total_amount'] - 1126.0) < 0.01:
                print(f"  🎯 THIS MATCHES THE AMOUNT IN THE IMAGE! (1126 บาท)")
                
                # Get detailed items for this order
                try:
                    cursor.execute("""
                        SELECT oi.*, mi.name as item_name, mi.price as item_price
                        FROM order_items oi
                        JOIN menu_items mi ON oi.item_id = mi.item_id
                        WHERE oi.order_id = ?
                    """, (order['order_id'],))
                    
                    items = cursor.fetchall()
                    print(f"    Items in this order:")
                    for item in items:
                        item_subtotal = item['quantity'] * item['item_price']
                        print(f"      - {item['item_name']}: {item['quantity']}x {item['item_price']} = {item_subtotal} บาท")
                        
                except Exception as e:
                    print(f"    Error getting items: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_active_orders()