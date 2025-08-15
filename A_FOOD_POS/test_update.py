import sqlite3

# Test database update directly
conn = sqlite3.connect('FOOD_POS/pos_database.db')
cursor = conn.cursor()

# Check current value
print("Before update:")
cursor.execute('SELECT item_id, name, food_option_type FROM menu_items WHERE item_id = 344')
result = cursor.fetchone()
print(f"Database result: {result}")

# Update directly
print("\nUpdating food_option_type to 'sweet'...")
cursor.execute('''
    UPDATE menu_items 
    SET food_option_type = ?, updated_at = CURRENT_TIMESTAMP
    WHERE item_id = ?
''', ('sweet', 344))
conn.commit()

# Check after update
print("\nAfter update:")
cursor.execute('SELECT item_id, name, food_option_type FROM menu_items WHERE item_id = 344')
result = cursor.fetchone()
print(f"Database result: {result}")

conn.close()
print("\nDirect database update completed.")