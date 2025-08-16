import sqlite3

# เชื่อมต่อฐานข้อมูลในโฟลเดอร์ parent
conn = sqlite3.connect('../pos_database.db')
cursor = conn.cursor()

print("=== ตรวจสอบ Menu Items ===")

# ตรวจสอบ menu items ที่มีอยู่
cursor.execute('SELECT item_id, name, price FROM menu_items ORDER BY item_id LIMIT 10')
items = cursor.fetchall()

print(f"\nMenu items ที่มีอยู่ ({len(items)} รายการแรก):")
for item in items:
    print(f"  ID: {item[0]}, Name: {item[1]}, Price: {item[2]}")

if len(items) == 0:
    print("ไม่พบ menu items ในฐานข้อมูล!")
else:
    # ทดสอบสร้าง order ใหม่ด้วย item_id ที่มีอยู่จริง
    first_item_id = items[0][0]
    print(f"\nจะทดสอบสร้าง order ด้วย item_id: {first_item_id}")

conn.close()
print("\nเสร็จสิ้นการตรวจสอบ")