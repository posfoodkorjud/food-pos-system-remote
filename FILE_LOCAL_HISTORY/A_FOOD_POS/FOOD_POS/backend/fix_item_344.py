import sqlite3

# เชื่อมต่อฐานข้อมูลในโฟลเดอร์ parent
conn = sqlite3.connect('../pos_database.db')
cursor = conn.cursor()

print("=== แก้ไข Menu Item 344 ===\n")

# ตรวจสอบสถานะปัจจุบัน
cursor.execute('SELECT item_id, name, is_available FROM menu_items WHERE item_id = 344')
result = cursor.fetchone()
if result:
    print(f"ก่อนแก้ไข - Item 344: {result[1]}, is_available = {result[2]}")
else:
    print("ไม่พบ Item 344")
    conn.close()
    exit()

# อัปเดต is_available เป็น 1
cursor.execute('UPDATE menu_items SET is_available = 1 WHERE item_id = 344')
conn.commit()
print(f"อัปเดตแล้ว {cursor.rowcount} รายการ")

# ตรวจสอบหลังแก้ไข
cursor.execute('SELECT item_id, name, is_available FROM menu_items WHERE item_id = 344')
result = cursor.fetchone()
if result:
    print(f"หลังแก้ไข - Item 344: {result[1]}, is_available = {result[2]}")

conn.close()
print("\nเสร็จสิ้นการแก้ไข")