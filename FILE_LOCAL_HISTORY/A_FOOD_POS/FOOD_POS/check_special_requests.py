import sqlite3

def check_customer_requests():
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    # ตรวจสอบข้อมูล customer_request ที่มีอยู่
    cursor.execute('''
        SELECT order_item_id, order_id, customer_request 
        FROM order_items 
        WHERE customer_request IS NOT NULL AND customer_request != '' 
        LIMIT 10
    ''')
    
    print('Orders with customer_request:')
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f'Item ID: {row[0]}, Order ID: {row[1]}, customer_request: "{row[2]}"')
    else:
        print('No orders with customer_request found')
    
    # ตรวจสอบข้อมูลล่าสุด 5 รายการ
    cursor.execute('SELECT order_item_id, order_id, customer_request FROM order_items ORDER BY order_item_id DESC LIMIT 5')
    recent_rows = cursor.fetchall()
    print('\nRecent 5 orders:')
    for row in recent_rows:
        print(f'Item ID: {row[0]}, Order ID: {row[1]}, customer_request: "{row[2]}"')
    
    conn.close()

if __name__ == '__main__':
    check_customer_requests()