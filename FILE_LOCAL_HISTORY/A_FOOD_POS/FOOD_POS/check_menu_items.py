import sqlite3

conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

# Print all menu items with name and food_option_type
cursor.execute('SELECT name, food_option_type FROM menu_items')
items = cursor.fetchall()
print('Menu items (name, food_option_type):')
for item in items:
    print(item)

# Check menu categories
cursor.execute('SELECT * FROM menu_categories')
categories = cursor.fetchall()
print('\nMenu categories:')
for category in categories:
    print(category)

conn.close()