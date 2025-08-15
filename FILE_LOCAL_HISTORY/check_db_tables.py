import sqlite3

# Connect to database
conn = sqlite3.connect('A_FOOD_POS/FOOD_POS/pos_database.db')
cursor = conn.cursor()

print("=== Checking Database Tables ===")

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Available tables:")
for table in tables:
    print(f"- {table[0]}")

# Check structure of each table
for table in tables:
    table_name = table[0]
    print(f"\n=== Structure of {table_name} ===")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Show sample data
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
    rows = cursor.fetchall()
    if rows:
        print(f"\nSample data from {table_name}:")
        for row in rows:
            print(f"  {row}")
    else:
        print(f"\nNo data in {table_name}")

conn.close()