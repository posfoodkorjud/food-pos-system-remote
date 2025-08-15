import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('pos_database.db')
        cursor = conn.cursor()
        
        # ตรวจสอบตารางที่มีอยู่
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print('ตารางที่มีอยู่ในฐานข้อมูล:')
        for table in tables:
            print(f'- {table[0]}')
        
        # ตรวจสอบโครงสร้างตาราง menu_items
        try:
            cursor.execute("PRAGMA table_info(menu_items);")
            columns = cursor.fetchall()
            print('\nโครงสร้างตาราง menu_items:')
            for col in columns:
                print(f'- {col[1]} ({col[2]})')
        except Exception as e:
            print(f'ไม่สามารถตรวจสอบโครงสร้างตาราง menu_items: {e}')
        
        # ตรวจสอบจำนวนเมนูทั้งหมด
        try:
            cursor.execute('SELECT COUNT(*) FROM menu_items')
            menu_count = cursor.fetchone()[0]
            print(f'\nจำนวนเมนูทั้งหมด: {menu_count}')
        except Exception as e:
            print(f'ไม่สามารถนับจำนวนเมนู: {e}')
        
        # ตรวจสอบโครงสร้างตาราง menu_categories
        try:
            cursor.execute("PRAGMA table_info(menu_categories);")
            columns = cursor.fetchall()
            print('\nโครงสร้างตาราง menu_categories:')
            for col in columns:
                print(f'- {col[1]} ({col[2]})')
        except Exception as e:
            print(f'ไม่สามารถตรวจสอบโครงสร้างตาราง menu_categories: {e}')
        
        # ตรวจสอบจำนวนหมวดหมู่
        try:
            cursor.execute('SELECT COUNT(*) FROM menu_categories')
            category_count = cursor.fetchone()[0]
            print(f'\nจำนวนหมวดหมู่ทั้งหมด: {category_count}')
            
            # แสดงหมวดหมู่ที่มีอยู่
            cursor.execute('SELECT * FROM menu_categories')
            categories = cursor.fetchall()
            print('\nหมวดหมู่ที่มีอยู่:')
            for cat in categories:
                print(f'- {cat}')
        except Exception as e:
            print(f'ไม่สามารถนับจำนวนหมวดหมู่: {e}')
            
        # ตรวจสอบตาราง tables
        try:
            cursor.execute('SELECT COUNT(*) FROM tables')
            table_count = cursor.fetchone()[0]
            print(f'\nจำนวนโต๊ะทั้งหมด: {table_count}')
        except Exception as e:
            print(f'ไม่สามารถนับจำนวนโต๊ะ: {e}')
        
        conn.close()
        
    except Exception as e:
        print(f'เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล: {e}')

if __name__ == '__main__':
    check_database()