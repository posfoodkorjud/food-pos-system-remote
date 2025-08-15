import sqlite3

def check_customer_requests():
    conn = sqlite3.connect('pos_database.db')
    cursor = conn.cursor()
    
    # ตรวจสอบข้อมูล customer_request ที่มีอยู่
    print("=== Customer Requests ในฐานข้อมูล ===")
    cursor.execute("""
        SELECT DISTINCT customer_request 
        FROM order_items 
        WHERE customer_request IS NOT NULL 
        AND customer_request != '' 
        LIMIT 20
    """)
    
    rows = cursor.fetchall()
    if rows:
        print(f"พบ customer_request ทั้งหมด {len(rows)} รูปแบบ:")
        for i, row in enumerate(rows, 1):
            print(f"{i}. '{row[0]}'")
    else:
        print("ไม่พบข้อมูล customer_request ในฐานข้อมูล")
    
    # ตรวจสอบรูปแบบของ customer_request
    print("\n=== วิเคราะห์รูปแบบ customer_request ===")
    cursor.execute("""
        SELECT customer_request, COUNT(*) as count
        FROM order_items 
        WHERE customer_request IS NOT NULL 
        AND customer_request != '' 
        GROUP BY customer_request
        ORDER BY count DESC
        LIMIT 10
    """)
    
    rows = cursor.fetchall()
    if rows:
        print("รูปแบบที่พบบ่อยที่สุด:")
        for row in rows:
            print(f"- '{row[0]}' (ใช้ {row[1]} ครั้ง)")
            
            # วิเคราะห์รูปแบบ
            if ' | ' in row[0]:
                parts = row[0].split(' | ')
                print(f"  → แยกเป็น: {parts}")
    
    # ตรวจสอบข้อมูลล่าสุด
    print("\n=== ข้อมูล customer_request ล่าสุด 5 รายการ ===")
    cursor.execute("""
        SELECT order_item_id, customer_request, created_at
        FROM order_items 
        WHERE customer_request IS NOT NULL 
        AND customer_request != '' 
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Request: '{row[1]}', เวลา: {row[2]}")
    
    conn.close()

if __name__ == "__main__":
    check_customer_requests()