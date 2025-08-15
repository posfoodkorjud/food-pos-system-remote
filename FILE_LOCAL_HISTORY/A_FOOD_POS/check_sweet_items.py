import sqlite3

conn = sqlite3.connect('FOOD_POS/pos_database.db')
cursor = conn.cursor()

# ตรวจสอบเมนูที่มี food_option_type เป็น 'sweet'
cursor.execute('SELECT item_id, name, food_option_type FROM menu_items WHERE food_option_type = "sweet" AND is_available = 1')
items = cursor.fetchall()

print('เมนูที่มีตัวเลือกความหวาน:')
for item in items:
    print(f'ID: {item[0]}, Name: {item[1]}, Type: {item[2]}')

# ตรวจสอบเมนูทั้งหมดที่มี food_option_type ไม่ใช่ 'none'
cursor.execute('SELECT item_id, name, food_option_type FROM menu_items WHERE food_option_type != "none" AND is_available = 1')
all_option_items = cursor.fetchall()

print('\nเมนูทั้งหมดที่มีตัวเลือก:')
for item in all_option_items:
    print(f'ID: {item[0]}, Name: {item[1]}, Type: {item[2]}')

conn.close()