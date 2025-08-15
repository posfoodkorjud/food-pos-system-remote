import sqlite3

conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

# Check dessert category with ID 736
cursor.execute('SELECT category_id, name, description FROM menu_categories WHERE category_id = 736')
category = cursor.fetchone()
print('Dessert category 736:')
print(category)

# Check menu items for category 736
cursor.execute('SELECT item_id, name, price, description, is_available FROM menu_items WHERE category_id = 736')
items = cursor.fetchall()
print('\nMenu items for category 736:')
for item in items:
    print(item)

conn.close()