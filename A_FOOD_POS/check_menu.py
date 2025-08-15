import sqlite3

conn = sqlite3.connect('FOOD_POS/pos_database.db')
cursor = conn.cursor()

cursor.execute('SELECT item_id, name, category_id, price, is_available FROM menu_items WHERE is_available = 1 LIMIT 10')
rows = cursor.fetchall()

print("Available menu items:")
for row in rows:
    print(row)

conn.close()