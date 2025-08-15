import sqlite3

# เชื่อมต่อฐานข้อมูลในโฟลเดอร์ parent
conn = sqlite3.connect('../pos_database.db')
cursor = conn.cursor()

print("=== ตรวจสอบ Order ID 59 ===")

# ตรวจสอบ order 59
cursor.execute('SELECT * FROM orders WHERE order_id = 59')
order = cursor.fetchone()
if order:
    print(f"Order 59: Table {order[1]}, Session {order[2]}, Status {order[3]}, Total {order[4]}, Created {order[5]}")
else:
    print("ไม่พบ Order ID 59")

# ตรวจสอบ order_items ของ order 59
cursor.execute('SELECT * FROM order_items WHERE order_id = 59')
items = cursor.fetchall()
print(f"\nOrder items สำหรับ Order 59: {len(items)} รายการ")
for item in items:
    print(f"  - Item ID: {item[2]}, Qty: {item[3]}, Price: {item[4]}, Special: '{item[6]}'")

if len(items) == 0:
    print("ไม่พบ order_items สำหรับ Order 59 - นี่คือปัญหา!")
    
    # ตรวจสอบว่ามี menu item ID 1 หรือไม่
    cursor.execute('SELECT * FROM menu_items WHERE item_id = 1')
    menu_item = cursor.fetchone()
    if menu_item:
        print(f"\nMenu item ID 1 มีอยู่: {menu_item[1]} - ราคา {menu_item[2]}")
    else:
        print("\nไม่พบ Menu item ID 1 - นี่อาจเป็นสาเหตุ!")

conn.close()
print("\nเสร็จสิ้นการตรวจสอบ")