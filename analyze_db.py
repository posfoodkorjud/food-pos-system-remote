import sqlite3
import os

def analyze_database():
    # Check multiple possible database locations
    db_paths = [
        'A_FOOD_POS/FOOD_POS/backend/pos_database.db',
        'backend/pos_database.db',
        'A_FOOD_POS/pos_database.db',
        'pos_database.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("Database file not found in any of these locations:")
        for path in db_paths:
            print(f"  - {path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n=== Database Analysis: {db_path} ===")
        print(f"Total tables: {len(tables)}")
        print("\nTables found:")
        
        for table in tables:
            table_name = table[0]
            print(f"\n📋 Table: {table_name}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print(f"   Columns ({len(columns)}):")
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                is_pk = " (PRIMARY KEY)" if col[5] else ""
                print(f"   - {col_name}: {col_type}{is_pk}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            print(f"   Rows: {row_count}")
        
        conn.close()
        print("\n=== Analysis Complete ===")
        
    except Exception as e:
        print(f"Error analyzing database: {e}")

if __name__ == "__main__":
    analyze_database()