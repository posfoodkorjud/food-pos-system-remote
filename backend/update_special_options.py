import sqlite3

db = sqlite3.connect('pos_database.db')
c = db.cursor()
c.execute("UPDATE menu_items SET food_option_type='special' WHERE name LIKE '%ข้าว%' OR name LIKE '%ไข่%'")
db.commit()
print('Updated menu_items with special options.')
db.close()