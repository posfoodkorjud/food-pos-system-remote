import sqlite3

conn = sqlite3.connect('FOOD_POS/pos_database.db')
cursor = conn.cursor()

# ตรวจสอบเมนู ID 344 (กล้วยทอด)
cursor.execute('SELECT item_id, name, food_option_type FROM menu_items WHERE item_id = 344')
item = cursor.fetchone()

print(f'เมนู ID 344: {item}')

conn.close()