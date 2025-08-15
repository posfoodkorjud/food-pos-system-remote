import sqlite3

conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

# ตรวจสอบเมนูที่มี food_option_type ไม่ใช่ 'none'
cursor.execute('SELECT item_id, name, food_option_type FROM menu_items WHERE food_option_type != "none" LIMIT 10')
items = cursor.fetchall()

print('เมนูที่มีตัวเลือกพิเศษ:')
for item in items:
    print(f'ID: {item[0]}, Name: {item[1]}, Type: {item[2]}')

# ตรวจสอบเมนูที่มี food_option_type เป็น 'special'
cursor.execute('SELECT item_id, name, food_option_type FROM menu_items WHERE food_option_type LIKE "%special%"')
special_items = cursor.fetchall()

print('\nเมนูที่มีตัวเลือก special:')
for item in special_items:
    print(f'ID: {item[0]}, Name: {item[1]}, Type: {item[2]}')

# ตรวจสอบ option_values ที่มี option_type เป็น 'addon'
cursor.execute('SELECT * FROM option_values WHERE option_type = "addon"')
addon_options = cursor.fetchall()

print('\nตัวเลือก addon ที่มีอยู่:')
for option in addon_options:
    print(f'ID: {option[0]}, Type: {option[1]}, Name: {option[2]}, Price: {option[3]}')

conn.close()