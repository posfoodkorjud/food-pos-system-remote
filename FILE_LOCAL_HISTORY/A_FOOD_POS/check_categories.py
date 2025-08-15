import sqlite3

conn = sqlite3.connect('FOOD_POS/pos_database.db')
cursor = conn.cursor()

cursor.execute('SELECT category_id, name, description FROM menu_categories WHERE is_active = 1')
rows = cursor.fetchall()

print("Available menu categories:")
for row in rows:
    print(row)

conn.close()