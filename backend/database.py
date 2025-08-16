# -*- coding: utf-8 -*-
"""
Database Manager สำหรับระบบ POS ร้านอาหาร
ใช้ SQLite เป็นฐานข้อมูลหลัก
"""

import sqlite3
import os
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple
from models import Table, MenuCategory, MenuItem, Order, OrderItem, Receipt, SystemConfig
import pytz

# Import Google Sheets integration
try:
    from .google_sheets import is_google_sheets_enabled
    from .new_google_sheets_sync import sync_order_to_new_format
except ImportError:
    print("Warning: Google Sheets integration not available")
    def sync_order_to_new_format(*args, **kwargs):
        return False
    def is_google_sheets_enabled():
        return False

# ฟังก์ชันสำหรับจัดการเวลาท้องถิ่นของไทย
def get_thai_datetime():
    """ได้รับเวลาปัจจุบันในโซนเวลาไทย"""
    thai_tz = pytz.timezone('Asia/Bangkok')
    return datetime.now(thai_tz)

def get_thai_datetime_string():
    """ได้รับเวลาปัจจุบันในโซนเวลาไทยในรูปแบบ string"""
    return get_thai_datetime().strftime('%Y-%m-%d %H:%M:%S')

class DatabaseManager:
    """คลาสจัดการฐานข้อมูล SQLite"""
    
    def __init__(self, db_path: str = "pos_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """สร้างการเชื่อมต่อฐานข้อมูล"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # ให้ผลลัพธ์เป็น dict-like
        return conn
    
    def initialize_database(self):
        """สร้างตารางฐานข้อมูลเริ่มต้นและข้อมูลตัวอย่าง"""
        self.init_database()
        # สร้างค่าตัวเลือกเริ่มต้น
        self.initialize_default_option_values()
        # Disabled _insert_sample_data to prevent duplicate data
        # self._insert_sample_data()
    
    def init_database(self):
        """สร้างตารางฐานข้อมูลเริ่มต้น"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # ตารางโต๊ะ
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables (
                table_id INTEGER PRIMARY KEY,
                table_name TEXT NOT NULL,
                status TEXT DEFAULT 'available',
                qr_code TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตารางหมวดหมู่เมนู
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตารางเมนูอาหาร
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category_id INTEGER,
                description TEXT,
                image_url TEXT,
                is_available BOOLEAN DEFAULT 1,
                preparation_time INTEGER DEFAULT 15,
                food_option_type TEXT DEFAULT 'none',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES menu_categories (category_id)
            )
        ''')
        
        # อัปเดตโครงสร้างตารางถ้าจำเป็น
        try:
            # ตรวจสอบว่ามีคอลัมน์ food_option_type หรือไม่
            cursor.execute("PRAGMA table_info(menu_items)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'food_option_type' not in columns:
                # เพิ่มคอลัมน์ food_option_type
                cursor.execute('ALTER TABLE menu_items ADD COLUMN food_option_type TEXT DEFAULT "none"')
                
                # อัปเดตข้อมูลเดิมจาก spice_options และ sweetness_options
                cursor.execute('''
                    UPDATE menu_items 
                    SET food_option_type = CASE 
                        WHEN spice_options IS NOT NULL AND spice_options != '' THEN 'spice'
                        WHEN sweetness_options IS NOT NULL AND sweetness_options != '' THEN 'sweet'
                        ELSE 'none'
                    END
                ''')
                
                # ลบคอลัมน์เก่า (SQLite ไม่รองรับ DROP COLUMN โดยตรง)
                # เราจะปล่อยให้คอลัมน์เก่าอยู่เพื่อความปลอดภัย
            
            # ตรวจสอบว่ามีคอลัมน์ sort_order ในตาราง menu_categories หรือไม่
            cursor.execute("PRAGMA table_info(menu_categories)")
            category_columns = [column[1] for column in cursor.fetchall()]
            
            if 'sort_order' not in category_columns:
                # เพิ่มคอลัมน์ sort_order
                cursor.execute('ALTER TABLE menu_categories ADD COLUMN sort_order INTEGER DEFAULT 0')
                
                # อัปเดตลำดับเริ่มต้นตาม category_id
                cursor.execute('''
                    UPDATE menu_categories 
                    SET sort_order = category_id * 10
                    WHERE sort_order = 0 OR sort_order IS NULL
                ''')
            
            # ตรวจสอบว่ามีคอลัมน์ bill_status ในตาราง orders หรือไม่
            cursor.execute("PRAGMA table_info(orders)")
            order_columns = [column[1] for column in cursor.fetchall()]
            
            if 'bill_status' not in order_columns:
                # เพิ่มคอลัมน์ bill_status
                cursor.execute('ALTER TABLE orders ADD COLUMN bill_status TEXT DEFAULT "unchecked"')
                
                # อัปเดตข้อมูลเดิมให้มีสถานะ unchecked
                cursor.execute('''
                    UPDATE orders 
                    SET bill_status = "unchecked"
                    WHERE bill_status IS NULL
                ''')
            
            # ตรวจสอบว่ามีคอลัมน์ checkout_at ในตาราง tables หรือไม่
            cursor.execute("PRAGMA table_info(tables)")
            table_columns = [column[1] for column in cursor.fetchall()]
            
            if 'checkout_at' not in table_columns:
                # เพิ่มคอลัมน์ checkout_at สำหรับเก็บเวลาเช็คบิล
                cursor.execute('ALTER TABLE tables ADD COLUMN checkout_at TIMESTAMP')
                
        except Exception as e:
            print(f"Warning: Could not update table structure: {e}")
        
        # ตารางออเดอร์
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER,
                session_id TEXT,
                status TEXT DEFAULT 'active',
                bill_status TEXT DEFAULT 'unchecked',
                total_amount REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (table_id) REFERENCES tables (table_id)
            )
        ''')
        
        # ตารางรายการสั่งอาหาร
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                item_id INTEGER,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                customer_request TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (order_id),
                FOREIGN KEY (item_id) REFERENCES menu_items (item_id)
            )
        ''')
        
        # ตารางใบเสร็จ
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipts (
                receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                table_id INTEGER,
                total_amount REAL NOT NULL,
                payment_method TEXT DEFAULT 'promptpay',
                promptpay_qr TEXT,
                is_paid BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                paid_at TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (order_id),
                FOREIGN KEY (table_id) REFERENCES tables (table_id)
            )
        ''')
        
        # ตารางประวัติคำสั่งซื้อ (order_history)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_history (
                order_id INTEGER PRIMARY KEY,
                table_id INTEGER,
                session_id TEXT,
                status TEXT DEFAULT 'completed',
                total_amount REAL DEFAULT 0,
                created_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (table_id) REFERENCES tables (table_id)
            )
        ''')
        
        # ตารางรายการสินค้าในประวัติคำสั่งซื้อ (order_history_items)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_history_items (
                history_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                menu_item_id INTEGER,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                customer_request TEXT,
                status TEXT DEFAULT 'completed',
                FOREIGN KEY (order_id) REFERENCES order_history (order_id),
                FOREIGN KEY (menu_item_id) REFERENCES menu_items (menu_item_id)
            )
        ''')
        
        # ตารางการตั้งค่าระบบ
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                config_key TEXT PRIMARY KEY,
                config_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตารางการแจ้งเตือน
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER,
                message TEXT NOT NULL,
                type TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP,
                FOREIGN KEY (table_id) REFERENCES tables (table_id)
            )
        ''')
        
        # ตารางประเภทตัวเลือก (option types)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS option_types (
                option_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                key TEXT NOT NULL UNIQUE,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตารางค่าตัวเลือก (option values)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS option_values (
                option_value_id INTEGER PRIMARY KEY AUTOINCREMENT,
                option_type TEXT NOT NULL,
                name TEXT NOT NULL,
                additional_price DECIMAL(10,2) DEFAULT 0,
                is_default BOOLEAN DEFAULT 0,
                sort_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # สร้างดัชนีสำหรับค้นหาเร็วขึ้น
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_option_types_key ON option_types(key)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_option_values_type ON option_values(option_type)')
        
        conn.commit()
        conn.close()
        
        # ตรวจสอบว่ามีข้อมูลโต๊ะหรือไม่ ถ้าไม่มีให้สร้างโต๊ะเริ่มต้น
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM tables')
        count = cursor.fetchone()['count']
        conn.close()
        
        if count == 0:
            # สร้างโต๊ะเริ่มต้น 10 โต๊ะ
            for i in range(1, 11):
                self.add_table(i, f"โต๊ะ {i}")
    
    def init_default_data(self):
        """เพิ่มข้อมูลเริ่มต้น"""
        # สร้างโต๊ะเริ่มต้น 10 โต๊ะ
        for i in range(1, 11):
            self.add_table(i, f"โต๊ะ {i}")

    def save_setting(self, key: str, value: str):
        """บันทึกหรืออัปเดตการตั้งค่าใน system_config"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO system_config (config_key, config_value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(config_key) DO UPDATE SET
                    config_value = excluded.config_value,
                    updated_at = CURRENT_TIMESTAMP
            ''', (key, value))
            conn.commit()
        finally:
            conn.close()
        
        # สร้างหมวดหมู่เมนูเริ่มต้น
        default_categories = [
            ("อาหารจานเดียว", "ข้าวผัด ข้าวคลุกกะปิ ผัดไทย"),
            ("อาหารตามสั่ง", "ผัดผัก เนื้อผัด ไก่ผัด"),
            ("เครื่องดื่มร้อน", "กาแฟ ชา โกโก้"),
            ("เครื่องดื่มเย็น", "น้ำผลไม้ น้ำอัดลม สมูทตี้"),
            ("ของหวาน", "ไอศกรีม เค้ก ขนมไทย")
        ]
        
        for name, desc in default_categories:
            self.add_menu_category(name, desc)
        
        # สร้างเมนูตัวอย่าง
        sample_menu = [
            ("ข้าวผัดกุ้ง", 120, 1, "ข้าวผัดกุ้งสด พร้อมผักและไข่"),
            ("ผัดไทยกุ้งสด", 100, 1, "ผัดไทยแท้รสชาติดั้งเดิม"),
            ("ผัดกะเพราหมูสับ", 80, 2, "ผัดกะเพราหมูสับไข่ดาว"),
            ("ต้มยำกุ้ง", 150, 2, "ต้มยำกุ้งน้ำใส รสจัดจ้าน"),
            ("กาแฟร้อน", 45, 3, "กาแฟคั่วสด หอมกรุ่น"),
            ("ชาเย็น", 35, 4, "ชาเย็นหวานมัน"),
            ("ไอศกรีมวานิลลา", 60, 5, "ไอศกรีมวานิลลาเข้มข้น")
        ]
        
        for name, price, cat_id, desc in sample_menu:
            self.add_menu_item(name, price, cat_id, desc)
    
    # === Table Management ===
    def add_table(self, table_id: int, table_name: str) -> bool:
        """เพิ่มโต๊ะใหม่"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO tables (table_id, table_name)
                VALUES (?, ?)
            ''', (table_id, table_name))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding table: {e}")
            return False
    
    def get_all_tables(self) -> List[Dict]:
        """ดึงข้อมูลโต๊ะทั้งหมด"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tables ORDER BY table_id')
        tables = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tables
    
    def get_table(self, table_id: int) -> Dict:
        """ดึงข้อมูลโต๊ะตาม ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tables WHERE table_id = ?', (table_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_table_status(self, table_id: int, status: str, session_id: str = None) -> bool:
        """อัปเดตสถานะโต๊ะ"""
        try:
            # ดึงข้อมูลโต๊ะก่อนอัปเดตเพื่อเก็บ session_id เดิม
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT session_id FROM tables WHERE table_id = ?', (table_id,))
            row = cursor.fetchone()
            old_session_id = row['session_id'] if row else None
            
            print(f"[DEBUG] update_table_status: Updating table {table_id} from status to '{status}', session_id changing from '{old_session_id}' to '{session_id}'")
            
            # ถ้า session_id เป็น None ให้ล้างค่าในฐานข้อมูลอย่างชัดเจน
            if session_id is None:
                print(f"[DEBUG] update_table_status: Explicitly setting session_id to NULL for table {table_id}")
            
            cursor.execute('''
                UPDATE tables 
                SET status = ?, session_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE table_id = ?
            ''', (status, session_id, table_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating table status: {e}")
            return False
    
    def update_table_checkout_time(self, table_id: int) -> bool:
        """อัปเดตเวลาเช็คบิลของโต๊ะ"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tables 
                SET checkout_at = CURRENT_TIMESTAMP
                WHERE table_id = ?
            ''', (table_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating table checkout time: {e}")
            return False
    
    def delete_table(self, table_id: int) -> bool:
        """ลบโต๊ะ"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ตรวจสอบว่าโต๊ะมีออเดอร์ที่ยังไม่เสร็จสิ้นหรือไม่
            cursor.execute('''
                SELECT COUNT(*) as count FROM orders 
                WHERE table_id = ? AND status != 'completed'
            ''', (table_id,))
            count = cursor.fetchone()['count']
            
            if count > 0:
                print(f"Cannot delete table {table_id}: {count} pending orders exist")
                return False
            
            # ลบโต๊ะ
            cursor.execute('DELETE FROM tables WHERE table_id = ?', (table_id,))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting table: {e}")
            return False
    
    # === Menu Management ===
    def add_menu_category(self, name: str, description: str = "") -> int:
        """เพิ่มหมวดหมู่เมนู"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO menu_categories (name, description)
                VALUES (?, ?)
            ''', (name, description))
            category_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return category_id
        except Exception as e:
            print(f"Error adding menu category: {e}")
            return 0
    
    def get_menu_categories(self) -> List[Dict]:
        """ดึงหมวดหมู่เมนูทั้งหมด"""
        print("[DEBUG] get_menu_categories called")
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM menu_categories WHERE is_active = 1 ORDER BY sort_order, name')
        rows = cursor.fetchall()
        print(f"[DEBUG] Raw rows from database: {len(rows)}")
        categories = [dict(row) for row in rows]
        print(f"[DEBUG] Converted categories: {len(categories)}")
        if categories:
            print(f"[DEBUG] First category data: {categories[0]}")
        conn.close()
        return categories
    
    def add_menu_item(self, name: str, price: float, category_id: int, description: str = "", image_url: str = None, is_available: bool = True, preparation_time: int = 15, food_option_type: str = 'none') -> int:
        """เพิ่มเมนูอาหาร"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO menu_items (name, price, category_id, description, image_url, is_available, preparation_time, food_option_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, price, category_id, description, image_url, is_available, preparation_time, food_option_type))
            item_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return item_id
        except Exception as e:
            print(f"Error adding menu item: {e}")
            return 0
    
    def get_menu_items(self, category_id: int = None) -> List[Dict]:
        """ดึงเมนูอาหารทั้งหมดหรือตามหมวดหมู่"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        print(f"[DEBUG DB] get_menu_items called with category_id: {category_id}")
        
        if category_id:
            query = '''
                SELECT mi.*, mc.name as category_name 
                FROM menu_items mi
                JOIN menu_categories mc ON mi.category_id = mc.category_id
                WHERE mi.category_id = ? AND mi.is_available = 1
                ORDER BY mi.name
            '''
            print(f"[DEBUG DB] Executing query with category_id: {query}")
            cursor.execute(query, (category_id,))
        else:
            query = '''
                SELECT mi.*, mc.name as category_name 
                FROM menu_items mi
                JOIN menu_categories mc ON mi.category_id = mc.category_id
                WHERE mi.is_available = 1
                ORDER BY mc.category_id, mi.name
            '''
            print(f"[DEBUG DB] Executing query without category_id: {query}")
            cursor.execute(query)
        
        rows = cursor.fetchall()
        print(f"[DEBUG DB] Raw rows fetched: {len(rows)}")
        if rows:
            print(f"[DEBUG DB] First row: {dict(rows[0])}")
        
        items = [dict(row) for row in rows]
        print(f"[DEBUG DB] Final items count: {len(items)}")
        conn.close()
        return items
    
    def get_all_menu_items(self, category_id: int = None) -> List[Dict]:
        """ดึงเมนูอาหารทั้งหมดรวมถึงที่ปิดการใช้งาน (สำหรับหน้าจัดการเมนู)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        print(f"[DEBUG DB] get_all_menu_items called with category_id: {category_id}")
        
        if category_id:
            query = '''
                SELECT mi.*, mc.name as category_name 
                FROM menu_items mi
                JOIN menu_categories mc ON mi.category_id = mc.category_id
                WHERE mi.category_id = ?
                ORDER BY mi.name
            '''
            print(f"[DEBUG DB] Executing query with category_id: {query}")
            cursor.execute(query, (category_id,))
        else:
            query = '''
                SELECT mi.*, mc.name as category_name 
                FROM menu_items mi
                JOIN menu_categories mc ON mi.category_id = mc.category_id
                ORDER BY mc.category_id, mi.name
            '''
            print(f"[DEBUG DB] Executing query without category_id: {query}")
            cursor.execute(query)
        
        rows = cursor.fetchall()
        print(f"[DEBUG DB] Raw rows fetched (all items): {len(rows)}")
        if rows:
            print(f"[DEBUG DB] First row: {dict(rows[0])}")
        
        items = [dict(row) for row in rows]
        print(f"[DEBUG DB] Final items count (all items): {len(items)}")
        conn.close()
        return items
        
    def get_menu_item(self, item_id: int) -> Dict:
        """ดึงข้อมูลเมนูอาหารตาม ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mi.*, mc.name as category_name 
            FROM menu_items mi
            JOIN menu_categories mc ON mi.category_id = mc.category_id
            WHERE mi.item_id = ?
        ''', (item_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_menu_category(self, category_id: int, name: str, description: str = "") -> bool:
        """อัปเดตหมวดหมู่เมนู"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE menu_categories 
                SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE category_id = ?
            ''', (name, description, category_id))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating menu category: {e}")
            return False
    
    def delete_menu_category(self, category_id: int) -> bool:
        """ลบหมวดหมู่เมนู (soft delete)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # ตรวจสอบว่ามีเมนูในหมวดหมู่นี้หรือไม่
            cursor.execute('SELECT COUNT(*) as count FROM menu_items WHERE category_id = ? AND is_available = 1', (category_id,))
            count = cursor.fetchone()['count']
            
            if count > 0:
                print(f"Cannot delete category: {count} menu items still exist")
                return False
            
            cursor.execute('''
                UPDATE menu_categories 
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE category_id = ?
            ''', (category_id,))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting menu category: {e}")
            return False
    
    def update_category_sort_order(self, category_id: int, new_sort_order: int) -> bool:
        """อัปเดตลำดับการแสดงผลของหมวดหมู่"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE menu_categories 
                SET sort_order = ?
                WHERE category_id = ?
            ''', (new_sort_order, category_id))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating category sort order: {e}")
            return False
    
    def move_category_up(self, category_id: int) -> bool:
        """เลื่อนหมวดหมู่ขึ้น"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ดึงข้อมูลหมวดหมู่ปัจจุบัน
            cursor.execute('SELECT sort_order FROM menu_categories WHERE category_id = ?', (category_id,))
            current_row = cursor.fetchone()
            if not current_row:
                return False
            
            current_sort_order = current_row['sort_order']
            
            # หาหมวดหมู่ที่อยู่ข้างบนที่ใกล้ที่สุด
            cursor.execute('''
                SELECT category_id, sort_order 
                FROM menu_categories 
                WHERE sort_order < ? AND is_active = 1
                ORDER BY sort_order DESC 
                LIMIT 1
            ''', (current_sort_order,))
            
            prev_row = cursor.fetchone()
            if not prev_row:
                return False  # ไม่มีหมวดหมู่ข้างบน
            
            prev_category_id = prev_row['category_id']
            prev_sort_order = prev_row['sort_order']
            
            # สลับลำดับ
            cursor.execute('UPDATE menu_categories SET sort_order = ? WHERE category_id = ?', 
                         (prev_sort_order, category_id))
            cursor.execute('UPDATE menu_categories SET sort_order = ? WHERE category_id = ?', 
                         (current_sort_order, prev_category_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error moving category up: {e}")
            return False
    
    def move_category_down(self, category_id: int) -> bool:
        """เลื่อนหมวดหมู่ลง"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ดึงข้อมูลหมวดหมู่ปัจจุบัน
            cursor.execute('SELECT sort_order FROM menu_categories WHERE category_id = ?', (category_id,))
            current_row = cursor.fetchone()
            if not current_row:
                return False
            
            current_sort_order = current_row['sort_order']
            
            # หาหมวดหมู่ที่อยู่ข้างล่างที่ใกล้ที่สุด
            cursor.execute('''
                SELECT category_id, sort_order 
                FROM menu_categories 
                WHERE sort_order > ? AND is_active = 1
                ORDER BY sort_order ASC 
                LIMIT 1
            ''', (current_sort_order,))
            
            next_row = cursor.fetchone()
            if not next_row:
                return False  # ไม่มีหมวดหมู่ข้างล่าง
            
            next_category_id = next_row['category_id']
            next_sort_order = next_row['sort_order']
            
            # สลับลำดับ
            cursor.execute('UPDATE menu_categories SET sort_order = ? WHERE category_id = ?', 
                         (next_sort_order, category_id))
            cursor.execute('UPDATE menu_categories SET sort_order = ? WHERE category_id = ?', 
                         (current_sort_order, next_category_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error moving category down: {e}")
            return False
    
    def update_menu_item(self, item_id: int, name: str, price: float, category_id: int, description: str = "", image_url: str = None, is_available: bool = True, preparation_time: int = 15, food_option_type: str = 'none') -> bool:
        """อัปเดตเมนูอาหาร"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE menu_items 
                SET name = ?, price = ?, category_id = ?, description = ?, image_url = ?, 
                    is_available = ?, preparation_time = ?, food_option_type = ?, updated_at = CURRENT_TIMESTAMP
                WHERE item_id = ?
            ''', (name, price, category_id, description, image_url, is_available, preparation_time, food_option_type, item_id))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating menu item: {e}")
            return False
    
    def delete_menu_item(self, item_id: int) -> bool:
        """ลบเมนูอาหาร (hard delete)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ลบ menu item
            cursor.execute('DELETE FROM menu_items WHERE item_id = ?', (item_id,))
            
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting menu item: {e}")
            return False
    
    # === Order Management ===
    def create_order(self, table_id: int, session_id: str) -> int:
        """สร้างออเดอร์ใหม่"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            thai_time = get_thai_datetime_string()
            cursor.execute('''
                INSERT INTO orders (table_id, session_id, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (table_id, session_id, thai_time, thai_time))
            order_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return order_id
        except Exception as e:
            print(f"Error creating order: {e}")
            return 0
    
    def add_order_item(self, order_id: int, item_id: int, quantity: int, unit_price: float, customer_request: str = "") -> bool:
        try:
            print(f"[DEBUG] add_order_item called with: order_id={order_id}, item_id={item_id}, quantity={quantity}, unit_price={unit_price}, customer_request='{customer_request}'")
            total_price = quantity * unit_price
            print(f"[DEBUG] add_order_item: calculated total_price={total_price}")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ตรวจสอบว่า order_id มีอยู่จริงหรือไม่
            cursor.execute('SELECT order_id FROM orders WHERE order_id = ?', (order_id,))
            if not cursor.fetchone():
                print(f"[ERROR] add_order_item: Order ID {order_id} does not exist")
                conn.close()
                return False
            
            # ตรวจสอบว่า item_id มีอยู่จริงหรือไม่
            cursor.execute('SELECT item_id FROM menu_items WHERE item_id = ?', (item_id,))
            if not cursor.fetchone():
                print(f"[ERROR] add_order_item: Menu item ID {item_id} does not exist")
                conn.close()
                return False
            
            print(f"[DEBUG] add_order_item: Inserting into order_items...")
            thai_time = get_thai_datetime_string()
            cursor.execute('''
                INSERT INTO order_items (order_id, item_id, quantity, unit_price, total_price, customer_request, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, item_id, quantity, unit_price, total_price, customer_request, thai_time))
            
            order_item_id = cursor.lastrowid
            print(f"[DEBUG] add_order_item: Inserted order_item with ID={order_item_id}")
            
            # อัปเดตยอดรวมในออเดอร์ (ไม่รวมรายการที่ถูก reject)
            print(f"[DEBUG] add_order_item: Updating total_amount for order_id={order_id}")
            cursor.execute('''
                UPDATE orders 
                SET total_amount = (
                    SELECT COALESCE(SUM(total_price), 0) FROM order_items 
                    WHERE order_id = ? AND (status IS NULL OR status != 'rejected')
                ), updated_at = ?
                WHERE order_id = ?
            ''', (order_id, thai_time, order_id))
            
            # ตรวจสอบว่า update สำเร็จหรือไม่
            rows_affected = cursor.rowcount
            print(f"[DEBUG] add_order_item: Updated {rows_affected} rows in orders table")
            
            conn.commit()
            print(f"[DEBUG] add_order_item: Transaction committed successfully")
            conn.close()
            return True
        except Exception as e:
            print(f"[ERROR] add_order_item: {e}")
            import traceback
            print(f"[ERROR] add_order_item traceback: {traceback.format_exc()}")
            return False
    
    def get_table_orders(self, table_id: int, session_id: str = None) -> List[Dict]:
        """ดึงออเดอร์ของโต๊ะ (ทุกสถานะ)"""
        print(f"DEBUG: get_table_orders called with table_id={table_id}, session_id={session_id}")
        print(f"[DEBUG DETAIL] get_table_orders: session_id type: {type(session_id)}, value: '{session_id}'")
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # ตรวจสอบว่ามี session_id หรือไม่ (ต้องไม่เป็น None และไม่เป็นสตริงว่าง)
        if session_id is not None and session_id != '':
            print(f"[DEBUG DETAIL] get_table_orders: Using session_id filter: '{session_id}'")
            query = '''
                SELECT o.*, oi.*, mi.name as item_name, oi.status as item_status
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN menu_items mi ON oi.item_id = mi.item_id
                WHERE o.table_id = ? AND o.session_id = ?
                ORDER BY oi.created_at
            '''
            params = (table_id, session_id)
            print(f"DEBUG: Executing query with session_id: {query}")
            print(f"DEBUG: Parameters: {params}")
            cursor.execute(query, params)
        else:
            print(f"[DEBUG DETAIL] get_table_orders: No session_id provided, will return ALL orders for table {table_id}")
            query = '''
                SELECT o.*, oi.*, mi.name as item_name, oi.status as item_status
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN menu_items mi ON oi.item_id = mi.item_id
                WHERE o.table_id = ?
                ORDER BY oi.created_at
            '''
            params = (table_id,)
            print(f"DEBUG: Executing query without session_id: {query}")
            print(f"DEBUG: Parameters: {params}")
            cursor.execute(query, params)
        
        raw_results = cursor.fetchall()
        print(f"DEBUG: Raw query results count: {len(raw_results)}")
        if raw_results:
            first_result = dict(raw_results[0])
            print(f"DEBUG: First result: {first_result}")
            if 'session_id' in first_result:
                print(f"[DEBUG DETAIL] First result session_id: '{first_result['session_id']}'")
        
        orders = [dict(row) for row in raw_results]
        print(f"DEBUG: Final orders count: {len(orders)}")
        
        # แสดงข้อมูล session_id ของทุกรายการที่ได้
        if orders:
            session_ids = set(order.get('session_id') for order in orders if 'session_id' in order)
            print(f"[DEBUG DETAIL] Orders contain these session_ids: {session_ids}")
        
        conn.close()
        return orders
    
    def complete_payment_transaction(self, table_id: int, session_id: str) -> bool:
        """ดำเนินการชำระเงินแบบ transaction เดียว - ปิดออเดอร์และอัปเดตสถานะโต๊ะ"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # เริ่ม transaction
            cursor.execute('BEGIN TRANSACTION')
            
            # ดึงออเดอร์ของโต๊ะ
            cursor.execute('''
                SELECT order_id FROM orders 
                WHERE table_id = ? AND session_id = ? AND status = 'active'
            ''', (table_id, session_id))
            
            order_rows = cursor.fetchall()
            completed_orders = []
            
            # ปิดออเดอร์ทั้งหมด
            for order_row in order_rows:
                order_id = order_row[0]
                
                # อัปเดตสถานะออเดอร์
                cursor.execute('''
                    UPDATE orders 
                    SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                    WHERE order_id = ?
                ''', (order_id,))
                
                # ดึงข้อมูลออเดอร์สำหรับ Google Sheets
                cursor.execute('''
                    SELECT order_id, table_id, session_id, status, total_amount, 
                           created_at, completed_at, updated_at
                    FROM orders 
                    WHERE order_id = ?
                ''', (order_id,))
                
                order_data_row = cursor.fetchone()
                if order_data_row:
                    order_data = {
                        'order_id': order_data_row[0],
                        'table_id': order_data_row[1],
                        'session_id': order_data_row[2],
                        'status': order_data_row[3],
                        'total_amount': order_data_row[4],
                        'created_at': order_data_row[5],
                        'completed_at': order_data_row[6],
                        'updated_at': order_data_row[7]
                    }
                    
                    # ดึงรายการอาหารในออเดอร์
                    cursor.execute('''
                        SELECT oi.order_item_id, oi.order_id, oi.item_id, oi.quantity,
                               oi.unit_price, oi.total_price, oi.customer_request, oi.status,
                               mi.name as item_name
                        FROM order_items oi
                        LEFT JOIN menu_items mi ON oi.item_id = mi.item_id
                        WHERE oi.order_id = ?
                    ''', (order_id,))
                    
                    order_items = []
                    for item_row in cursor.fetchall():
                        order_items.append({
                            'order_item_id': item_row[0],
                            'order_id': item_row[1],
                            'item_id': item_row[2],
                            'quantity': item_row[3],
                            'unit_price': item_row[4],
                            'total_price': item_row[5],
                            'customer_request': item_row[6],
                            'status': item_row[7],
                            'item_name': item_row[8]
                        })
                    
                    # ตรวจสอบว่า order_id มีอยู่ใน order_history แล้วหรือไม่
                    cursor.execute('SELECT order_id FROM order_history WHERE order_id = ?', (order_data['order_id'],))
                    existing_order = cursor.fetchone()
                    
                    if not existing_order:
                        # ย้ายข้อมูลไปยัง order_history เฉพาะเมื่อยังไม่มี
                        cursor.execute('''
                            INSERT INTO order_history (order_id, table_id, session_id, status, total_amount, 
                                                      created_at, completed_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (order_data['order_id'], order_data['table_id'], order_data['session_id'], 
                              order_data['status'], order_data['total_amount'], order_data['created_at'], 
                              order_data['completed_at']))
                        
                        # ย้ายรายการอาหารไปยัง order_history_items เฉพาะเมื่อ order ใหม่
                        for item in order_items:
                            cursor.execute('''
                                INSERT INTO order_history_items (order_id, menu_item_id, quantity, price, customer_request, status)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (item['order_id'], item['item_id'], item['quantity'], item['unit_price'], 
                                  item['customer_request'], item['status']))
                    else:
                        print(f"[DEBUG] Order {order_data['order_id']} already exists in order_history, skipping")
                    
                    completed_orders.append((order_data, order_items))
            
            # อัปเดตสถานะโต๊ะเป็นรอเคลียร์โต๊ะ
            cursor.execute('''
                UPDATE tables 
                SET status = 'needs_clearing', updated_at = CURRENT_TIMESTAMP
                WHERE table_id = ?
            ''', (table_id,))
            
            # Commit transaction
            conn.commit()
            print(f"[DEBUG] complete_payment_transaction: Table {table_id} payment completed, {len(completed_orders)} orders processed")
            
            # บันทึกลง Google Sheets แบบ background (หลังจาก commit แล้ว)
            if completed_orders and is_google_sheets_enabled():
                import threading
                def sync_to_sheets():
                    for order_data, order_items in completed_orders:
                        try:
                            sync_success = sync_order_to_new_format(order_data, order_items)
                            if sync_success:
                                print(f"[Google Sheets] Order {order_data['order_id']} synced successfully")
                            else:
                                print(f"[Google Sheets] Failed to sync order {order_data['order_id']}")
                        except Exception as sheets_error:
                            print(f"[Google Sheets] Error syncing order {order_data['order_id']}: {sheets_error}")
                
                # รันการซิงค์ใน background thread
                sync_thread = threading.Thread(target=sync_to_sheets, daemon=True)
                sync_thread.start()
            
            return True
                
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error in complete_payment_transaction: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def complete_order(self, order_id: int) -> bool:
        """ปิดออเดอร์ (เก็บไว้เพื่อ backward compatibility)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # อัปเดตสถานะออเดอร์
            cursor.execute('''
                UPDATE orders 
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
            ''', (order_id,))
            
            # ดึงข้อมูลออเดอร์สำหรับ Google Sheets
            cursor.execute('''
                SELECT order_id, table_id, session_id, status, total_amount, 
                       created_at, completed_at, updated_at
                FROM orders 
                WHERE order_id = ?
            ''', (order_id,))
            
            order_row = cursor.fetchone()
            if order_row:
                order_data = {
                    'order_id': order_row[0],
                    'table_id': order_row[1],
                    'session_id': order_row[2],
                    'status': order_row[3],
                    'total_amount': order_row[4],
                    'created_at': order_row[5],
                    'completed_at': order_row[6],
                    'updated_at': order_row[7]
                }
                
                # ดึงรายการอาหารในออเดอร์
                cursor.execute('''
                    SELECT oi.order_item_id, oi.order_id, oi.item_id, oi.quantity,
                           oi.unit_price, oi.total_price, oi.customer_request, oi.status,
                           mi.name as item_name
                    FROM order_items oi
                    LEFT JOIN menu_items mi ON oi.item_id = mi.item_id
                    WHERE oi.order_id = ?
                ''', (order_id,))
                
                order_items = []
                for item_row in cursor.fetchall():
                    order_items.append({
                        'order_item_id': item_row[0],
                        'order_id': item_row[1],
                        'item_id': item_row[2],
                        'quantity': item_row[3],
                        'unit_price': item_row[4],
                        'total_price': item_row[5],
                        'customer_request': item_row[6],
                        'status': item_row[7],
                        'item_name': item_row[8]
                    })
                
                # ตรวจสอบว่า order_id มีอยู่ใน order_history แล้วหรือไม่
                cursor.execute('SELECT order_id FROM order_history WHERE order_id = ?', (order_data['order_id'],))
                existing_order = cursor.fetchone()
                
                if not existing_order:
                    # ย้ายข้อมูลไปยัง order_history เฉพาะเมื่อยังไม่มี
                    cursor.execute('''
                        INSERT INTO order_history (order_id, table_id, session_id, status, total_amount, 
                                                  created_at, completed_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (order_data['order_id'], order_data['table_id'], order_data['session_id'], 
                          order_data['status'], order_data['total_amount'], order_data['created_at'], 
                          order_data['completed_at']))
                    
                    # ย้ายรายการอาหารไปยัง order_history_items เฉพาะเมื่อ order ใหม่
                    for item in order_items:
                        cursor.execute('''
                            INSERT INTO order_history_items (order_id, menu_item_id, quantity, price, customer_request, status)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (item['order_id'], item['item_id'], item['quantity'], item['unit_price'], 
                              item['customer_request'], item['status']))
                else:
                    print(f"[DEBUG] Order {order_data['order_id']} already exists in order_history, skipping")
                
                conn.commit()
                conn.close()
                
                # บันทึกลง Google Sheets แบบ background (ไม่ให้ผู้ใช้รอ)
                if is_google_sheets_enabled():
                    import threading
                    def sync_to_sheets():
                        try:
                            sync_success = sync_order_to_new_format(order_data, order_items)
                            if sync_success:
                                print(f"[Google Sheets] Order {order_id} synced successfully")
                            else:
                                print(f"[Google Sheets] Failed to sync order {order_id}")
                        except Exception as sheets_error:
                            print(f"[Google Sheets] Error syncing order {order_id}: {sheets_error}")
                    
                    # รันการซิงค์ใน background thread
                    sync_thread = threading.Thread(target=sync_to_sheets, daemon=True)
                    sync_thread.start()
                
                return True
            else:
                conn.close()
                print(f"Error: Order {order_id} not found")
                return False
                
        except Exception as e:
            print(f"Error completing order: {e}")
            return False
    
    def update_order_status(self, order_id: int, status: str) -> bool:
        """อัปเดตสถานะออเดอร์"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE orders 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
            ''', (status, order_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False
    
    def update_order_item_status(self, order_item_id: int, status: str) -> bool:
        """อัปเดตสถานะรายการออเดอร์ย่อย และอัปเดต total_amount ของออเดอร์"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ดึง order_id ก่อนอัปเดต
            cursor.execute('SELECT order_id FROM order_items WHERE order_item_id = ?', (order_item_id,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False
            order_id = result['order_id']
            
            # อัปเดตสถานะรายการ
            cursor.execute('''
                UPDATE order_items 
                SET status = ?
                WHERE order_item_id = ?
            ''', (status, order_item_id))
            
            # อัปเดต total_amount ของออเดอร์โดยรวมเฉพาะรายการที่ไม่ถูกปฏิเสธ
            cursor.execute('''
                UPDATE orders 
                SET total_amount = (
                    SELECT COALESCE(SUM(total_price), 0) 
                    FROM order_items 
                    WHERE order_id = ? AND (status IS NULL OR status != 'rejected')
                ), updated_at = ?
                WHERE order_id = ?
            ''', (order_id, get_thai_datetime_string(), order_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating order item status: {e}")
            return False
    
    def get_order_items_with_status(self, order_id: int) -> List[Dict]:
        """ดึงรายการออเดอร์ย่อยพร้อมสถานะ"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT oi.order_item_id, oi.order_id, oi.item_id, oi.quantity, 
                       oi.unit_price, oi.customer_request, oi.status,
                       mi.name, mi.description
                FROM order_items oi
                JOIN menu_items mi ON oi.item_id = mi.item_id
                WHERE oi.order_id = ?
                ORDER BY oi.order_item_id
            ''', (order_id,))
            
            items = []
            for row in cursor.fetchall():
                items.append({
                    'order_item_id': row['order_item_id'],
                    'order_id': row['order_id'],
                    'item_id': row['item_id'],
                    'name': row['name'],
                    'description': row['description'],
                    'quantity': row['quantity'],
                    'unit_price': row['unit_price'],
                    'customer_request': row['customer_request'],
                    'status': row['status'] or 'pending'
                })
            
            conn.close()
            return items
        except Exception as e:
            print(f"Error getting order items with status: {e}")
            return []
    
    def get_orders_by_table(self, table_id: int, status: str = None) -> List[Dict]:
        """ดึงรายการคำสั่งซื้อของโต๊ะตามสถานะ"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # สร้างคำสั่ง SQL ตามเงื่อนไข
            query = '''
                SELECT o.order_id, o.table_id, o.session_id, o.status, datetime(o.created_at, 'localtime') as created_at,
                oi.order_item_id, oi.quantity, oi.unit_price, oi.customer_request,
                oi.status as item_status,
                mi.name as menu_name, mi.item_id, oi.unit_price as price
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN menu_items mi ON oi.item_id = mi.item_id
            WHERE o.table_id = ?
            '''
            
            params = [table_id]
            
            # เพิ่มเงื่อนไขสถานะถ้ามีการระบุ
            if status:
                query += ' AND oi.status = ?'
                params.append(status)
            
            query += ' ORDER BY o.created_at DESC, oi.order_item_id'
            
            cursor.execute(query, params)
            orders = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return orders
        except Exception as e:
            print(f"Error getting orders by table: {e}")
            return []
    
    def delete_orders_by_session(self, table_id: int, session_id: str) -> bool:
        """ลบออเดอร์ทั้งหมดของ session ที่ระบุ"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ดึงรายการ order_id ที่ต้องลบ
            cursor.execute('''
                SELECT order_id FROM orders 
                WHERE table_id = ? AND session_id = ?
            ''', (table_id, session_id))
            
            order_ids = [row['order_id'] for row in cursor.fetchall()]
            
            if order_ids:
                # ลบ order_items ก่อน
                placeholders = ','.join('?' * len(order_ids))
                cursor.execute(f'''
                    DELETE FROM order_items 
                    WHERE order_id IN ({placeholders})
                ''', order_ids)
                
                # ลบ orders
                cursor.execute('''
                    DELETE FROM orders 
                    WHERE table_id = ? AND session_id = ?
                ''', (table_id, session_id))
            
            conn.commit()
            conn.close()
            print(f"Deleted {len(order_ids)} orders for table {table_id}, session {session_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting orders by session: {e}")
            return False
    
    def get_orders_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """ดึงออเดอร์ตามช่วงวันที่"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT o.order_id, o.table_id, o.session_id, o.status, o.total_amount,
                       o.created_at, o.completed_at, t.table_name
                FROM orders o
                JOIN tables t ON o.table_id = t.table_id
                WHERE DATE(o.created_at) BETWEEN ? AND ?
                ORDER BY o.created_at DESC
            ''', (start_date, end_date))
            
            orders = []
            for row in cursor.fetchall():
                order_data = {
                    'order_id': row['order_id'],
                    'table_id': row['table_id'],
                    'table_name': row['table_name'],
                    'session_id': row['session_id'],
                    'status': row['status'],
                    'total_amount': row['total_amount'],
                    'created_at': row['created_at'],
                    'completed_at': row['completed_at']
                }
                
                # ดึงรายการอาหารของแต่ละออเดอร์
                cursor.execute('''
                    SELECT oi.order_item_id, oi.item_id, oi.quantity, oi.unit_price, 
                           oi.total_price, oi.customer_request, oi.status, mi.name as item_name
                    FROM order_items oi
                    JOIN menu_items mi ON oi.item_id = mi.item_id
                    WHERE oi.order_id = ?
                ''', (row['order_id'],))
                
                items = []
                recalculated_total = 0
                for item_row in cursor.fetchall():
                    item_status = item_row['status'] or 'pending'
                    item_data = {
                        'order_item_id': item_row['order_item_id'],
                        'item_id': item_row['item_id'],
                        'name': item_row['item_name'],
                        'quantity': item_row['quantity'],
                        'unit_price': item_row['unit_price'],
                        'total_price': item_row['total_price'],
                        'customer_request': item_row['customer_request'],
                        'status': item_status
                    }
                    items.append(item_data)
                    
                    # คำนวณยอดรวมใหม่โดยไม่รวมรายการที่ถูก reject
                    if item_status != 'rejected':
                        recalculated_total += item_row['total_price']
                
                # ใช้ยอดรวมที่คำนวณใหม่แทนที่จะใช้จากตาราง orders
                order_data['total_amount'] = recalculated_total
                order_data['items'] = items
                orders.append(order_data)
            
            conn.close()
            return orders
        except Exception as e:
            print(f"Error getting orders by date range: {e}")
            return []
    
    # === System Config ===
    def set_config(self, key: str, value: str) -> bool:
        """ตั้งค่าระบบ"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO system_config (config_key, config_value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error setting config: {e}")
            return False
    
    def get_config(self, key: str) -> str:
        """ดึงค่าการตั้งค่า"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT config_value FROM system_config WHERE config_key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result['config_value'] if result else ""
    
    def get_all_config(self) -> Dict:
        """ดึงการตั้งค่าทั้งหมด"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT config_key, config_value FROM system_config')
        config = {row['config_key']: row['config_value'] for row in cursor.fetchall()}
        conn.close()
        return config
    
    def _insert_sample_data(self):
        """เพิ่มข้อมูลตัวอย่างเริ่มต้น"""
        try:
            # เพิ่มโต๊ะตัวอย่าง
            for i in range(1, 11):
                self.add_table(i, f"โต๊ะ {i}")
            
            # เพิ่มหมวดหมู่เมนู
            categories = [
                ("อาหารจานหลัก", "อาหารจานหลักและข้าว"),
                ("เครื่องดื่ม", "เครื่องดื่มร้อนและเย็น"),
                ("ของหวาน", "ขนมหวานและของหวาน"),
                ("อาหารว่าง", "อาหารว่างและของทานเล่น")
            ]
            
            for name, desc in categories:
                self.add_menu_category(name, desc)
            
            # เพิ่มเมนูตัวอย่าง
            sample_items = [
                ("ข้าวผัดกุ้ง", 120.0, 1, "ข้าวผัดกุ้งสดใส่ไข่", None, True, 15),
                ("ผัดไทย", 80.0, 1, "ผัดไทยแท้รสชาติดั้งเดิม", None, True, 12),
                ("ต้มยำกุ้ง", 150.0, 1, "ต้มยำกุ้งน้ำใส รสเปรี้ยวจัด", None, True, 20),
                ("น้ำเปล่า", 15.0, 2, "น้ำดื่มบรรจุขวด", None, True, 1),
                ("โค้ก", 25.0, 2, "โคคาโคล่าเย็น", None, True, 1),
                ("กาแฟร้อน", 35.0, 2, "กาแฟดำร้อน", None, True, 5),
                ("ไอศกรีมวานิลลา", 45.0, 3, "ไอศกรีมวานิลลาเสิร์ฟเย็น", None, True, 3),
                ("ขนมปังปิ้ง", 30.0, 4, "ขนมปังปิ้งเนยน้ำผึ้ง", None, True, 8)
            ]
            
            for name, price, cat_id, desc, img, avail, prep_time in sample_items:
                self.add_menu_item(name, price, cat_id, desc, img, avail, prep_time)
            
            print("Sample data inserted successfully!")
            
        except Exception as e:
            print(f"Error inserting sample data: {e}")
    
    # === Notifications ===
    def save_notification(self, notification_data: Dict) -> bool:
        """บันทึกการแจ้งเตือน"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notifications (table_id, message, type, is_read)
                VALUES (?, ?, ?, ?)
            ''', (
                notification_data.get('table_id'),
                notification_data.get('message'),
                notification_data.get('type'),
                notification_data.get('is_read', False)
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving notification: {e}")
            return False
    
    def get_unread_notifications(self) -> List[Dict]:
        """ดึงการแจ้งเตือนที่ยังไม่ได้อ่าน"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT n.notification_id, n.table_id, n.message, n.type, 
                       n.is_read, n.created_at, t.table_name
                FROM notifications n
                LEFT JOIN tables t ON n.table_id = t.table_id
                WHERE n.is_read = 0
                ORDER BY n.created_at DESC
            ''')
            
            notifications = []
            for row in cursor.fetchall():
                notifications.append({
                    'notification_id': row['notification_id'],
                    'table_id': row['table_id'],
                    'table_name': row['table_name'],
                    'message': row['message'],
                    'type': row['type'],
                    'is_read': row['is_read'],
                    'created_at': row['created_at']
                })
            
            conn.close()
            return notifications
        except Exception as e:
            print(f"Error getting unread notifications: {e}")
            return []
    
    def mark_notification_read(self, notification_id: int) -> bool:
        """ทำเครื่องหมายการแจ้งเตือนว่าอ่านแล้ว"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE notifications 
                SET is_read = 1, read_at = CURRENT_TIMESTAMP
                WHERE notification_id = ?
            ''', (notification_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            return False
    
    def get_all_notifications(self, limit: int = 50) -> List[Dict]:
        """ดึงการแจ้งเตือนทั้งหมด"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT n.notification_id, n.table_id, n.message, n.type, 
                       n.is_read, n.created_at, n.read_at, t.table_name
                FROM notifications n
                LEFT JOIN tables t ON n.table_id = t.table_id
                ORDER BY n.created_at DESC
                LIMIT ?
            ''', (limit,))
            
            notifications = []
            for row in cursor.fetchall():
                notifications.append({
                    'notification_id': row['notification_id'],
                    'table_id': row['table_id'],
                    'table_name': row['table_name'],
                    'message': row['message'],
                    'type': row['type'],
                    'is_read': row['is_read'],
                    'created_at': row['created_at'],
                    'read_at': row['read_at']
                })
            
            conn.close()
            return notifications
        except Exception as e:
            print(f"Error getting all notifications: {e}")
            return []
    
    # ฟังก์ชันจัดการค่าตัวเลือก (Option Values)
    def get_option_values(self, option_type: str = None) -> List[Dict]:
        """ดึงค่าตัวเลือกทั้งหมดหรือตามประเภท"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if option_type:
                cursor.execute('''
                    SELECT * FROM option_values 
                    WHERE option_type = ? AND is_active = 1
                    ORDER BY sort_order, option_value_id
                ''', (option_type,))
            else:
                cursor.execute('''
                    SELECT * FROM option_values 
                    WHERE is_active = 1
                    ORDER BY option_type, sort_order, option_value_id
                ''')
            
            option_values = []
            for row in cursor.fetchall():
                option_values.append({
                    'option_value_id': row['option_value_id'],
                    'option_type': row['option_type'],
                    'name': row['name'],
                    'additional_price': float(row['additional_price']) if row['additional_price'] else 0,
                    'is_default': bool(row['is_default']),
                    'sort_order': row['sort_order'],
                    'is_active': bool(row['is_active']),
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            
            conn.close()
            return option_values
        except Exception as e:
            print(f"Error getting option values: {e}")
            return []
    
    def add_option_value(self, option_type: str, name: str, additional_price: float = 0, is_default: bool = False, sort_order: int = 0) -> bool:
        """เพิ่มค่าตัวเลือกใหม่"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ถ้าเป็นค่าเริ่มต้น ให้ยกเลิกค่าเริ่มต้นเดิม
            if is_default:
                cursor.execute('''
                    UPDATE option_values 
                    SET is_default = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE option_type = ?
                ''', (option_type,))
            
            # เพิ่มค่าตัวเลือกใหม่
            cursor.execute('''
                INSERT INTO option_values (option_type, name, additional_price, is_default, sort_order)
                VALUES (?, ?, ?, ?, ?)
            ''', (option_type, name, additional_price, is_default, sort_order))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding option value: {e}")
            return False
    
    def update_option_value(self, option_value_id: int, name: str = None, additional_price: float = None, is_default: bool = None, sort_order: int = None) -> bool:
        """อัปเดตค่าตัวเลือก"""
        try:
            print(f"DEBUG DB: Updating option_value_id {option_value_id}, name={name}, additional_price={additional_price}, is_default={is_default}, sort_order={sort_order}")
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ดึงข้อมูลเดิม
            cursor.execute('SELECT option_type FROM option_values WHERE option_value_id = ?', (option_value_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            option_type = result['option_type']
            
            # ถ้าเป็นค่าเริ่มต้น ให้ยกเลิกค่าเริ่มต้นเดิม
            if is_default:
                cursor.execute('''
                    UPDATE option_values 
                    SET is_default = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE option_type = ? AND option_value_id != ?
                ''', (option_type, option_value_id))
            
            # สร้างคำสั่ง UPDATE
            update_fields = []
            params = []
            
            if name is not None:
                update_fields.append('name = ?')
                params.append(name)
            
            if additional_price is not None:
                update_fields.append('additional_price = ?')
                params.append(additional_price)
            
            if is_default is not None:
                update_fields.append('is_default = ?')
                params.append(is_default)
            
            if sort_order is not None:
                update_fields.append('sort_order = ?')
                params.append(sort_order)
            
            if update_fields:
                update_fields.append('updated_at = CURRENT_TIMESTAMP')
                params.append(option_value_id)
                
                sql_query = f'''
                    UPDATE option_values 
                    SET {', '.join(update_fields)}
                    WHERE option_value_id = ?
                '''
                print(f"DEBUG DB: Executing SQL: {sql_query}")
                print(f"DEBUG DB: With params: {params}")
                
                cursor.execute(sql_query, params)
                
                # ตรวจสอบว่ามีการอัปเดตจริงหรือไม่
                rows_affected = cursor.rowcount
                print(f"DEBUG DB: Rows affected: {rows_affected}")
            
            conn.commit()
            conn.close()
            print(f"DEBUG DB: Update completed successfully")
            return True
        except Exception as e:
            print(f"Error updating option value: {e}")
            return False
    
    def delete_option_value(self, option_value_id: int) -> bool:
        """ลบค่าตัวเลือก (soft delete)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE option_values 
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE option_value_id = ?
            ''', (option_value_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting option value: {e}")
            return False
    
    def initialize_default_option_values(self):
        """สร้างค่าตัวเลือกเริ่มต้น"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ตรวจสอบและเพิ่มประเภทตัวเลือกเริ่มต้น
            cursor.execute('SELECT COUNT(*) as count FROM option_types')
            type_count = cursor.fetchone()['count']
            
            if type_count == 0:
                # เพิ่มประเภทตัวเลือกเริ่มต้น
                default_types = [
                    ('ระดับความเผ็ด', 'spice', 'ตัวเลือกสำหรับระดับความเผ็ดของอาหาร'),
                    ('ระดับความหวาน', 'sweet', 'ตัวเลือกสำหรับระดับความหวานของเครื่องดื่ม')
                ]
                
                for name, key, description in default_types:
                    cursor.execute('''
                        INSERT INTO option_types (name, key, description, is_active)
                        VALUES (?, ?, ?, ?)
                    ''', (name, key, description, True))
            
            # ตรวจสอบว่ามีข้อมูล option values อยู่แล้วหรือไม่
            cursor.execute('SELECT COUNT(*) as count FROM option_values')
            count = cursor.fetchone()['count']
            
            if count == 0:
                # เพิ่มค่าตัวเลือกความเผ็ด
                spice_options = [
                    ('ไม่เผ็ด', True, 1),
                    ('เผ็ดน้อย', False, 2),
                    ('เผ็ดปานกลาง', False, 3),
                    ('เผ็ดมาก', False, 4),
                    ('เผ็ดมากที่สุด', False, 5)
                ]
                
                for name, is_default, sort_order in spice_options:
                    cursor.execute('''
                        INSERT INTO option_values (option_type, name, is_default, sort_order)
                        VALUES (?, ?, ?, ?)
                    ''', ('spice', name, is_default, sort_order))
                
                # เพิ่มค่าตัวเลือกความหวาน
                sweet_options = [
                    ('ไม่หวาน', False, 1),
                    ('หวานน้อย', False, 2),
                    ('หวานปานกลาง', True, 3),
                    ('หวานมาก', False, 4)
                ]
                
                for name, is_default, sort_order in sweet_options:
                    cursor.execute('''
                        INSERT INTO option_values (option_type, name, is_default, sort_order)
                        VALUES (?, ?, ?, ?)
                    ''', ('sweet', name, is_default, sort_order))
                
                conn.commit()
            
            conn.close()
            return True
        except Exception as e:
            print(f"Error initializing default option values: {e}")
            return False
    
    def set_default_option_value(self, option_type: str, default_option_id: int) -> bool:
        """ตั้งค่าเริ่มต้นสำหรับตัวเลือก"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ยกเลิกค่าเริ่มต้นเดิมทั้งหมดในประเภทนี้
            cursor.execute('''
                UPDATE option_values 
                SET is_default = 0, updated_at = CURRENT_TIMESTAMP
                WHERE option_type = ?
            ''', (option_type,))
            
            # ตั้งค่าเริ่มต้นใหม่
            cursor.execute('''
                UPDATE option_values 
                SET is_default = 1, updated_at = CURRENT_TIMESTAMP
                WHERE option_value_id = ? AND option_type = ?
            ''', (default_option_id, option_type))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error setting default option value: {e}")
            return False
    
    # ฟังก์ชันจัดการประเภทตัวเลือก (Option Types)
    def get_option_types(self) -> List[Dict]:
        """ดึงประเภทตัวเลือกทั้งหมด"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM option_types 
                WHERE is_active = 1
                ORDER BY name
            ''')
            
            option_types = []
            for row in cursor.fetchall():
                option_types.append({
                    'option_type_id': row['option_type_id'],
                    'name': row['name'],
                    'key': row['key'],
                    'description': row['description'],
                    'is_active': bool(row['is_active']),
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            
            conn.close()
            return option_types
        except Exception as e:
            print(f"Error getting option types: {e}")
            return []
    
    def add_option_type(self, name: str, key: str, description: str = "", is_active: bool = True) -> bool:
        """เพิ่มประเภทตัวเลือกใหม่"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ตรวจสอบว่า key ซ้ำหรือไม่
            cursor.execute('SELECT COUNT(*) as count FROM option_types WHERE key = ?', (key,))
            if cursor.fetchone()['count'] > 0:
                conn.close()
                return False
            
            cursor.execute('''
                INSERT INTO option_types (name, key, description, is_active)
                VALUES (?, ?, ?, ?)
            ''', (name, key, description, is_active))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding option type: {e}")
            return False
    
    def update_option_type(self, option_type_id: int, name: str = None, description: str = None, is_active: bool = None) -> bool:
        """อัปเดตประเภทตัวเลือก"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # สร้างคำสั่ง UPDATE
            update_fields = []
            params = []
            
            if name is not None:
                update_fields.append('name = ?')
                params.append(name)
            
            if description is not None:
                update_fields.append('description = ?')
                params.append(description)
            
            if is_active is not None:
                update_fields.append('is_active = ?')
                params.append(is_active)
            
            if update_fields:
                update_fields.append('updated_at = CURRENT_TIMESTAMP')
                params.append(option_type_id)
                
                cursor.execute(f'''
                    UPDATE option_types 
                    SET {', '.join(update_fields)}
                    WHERE option_type_id = ?
                ''', params)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating option type: {e}")
            return False
    
    def delete_option_type(self, option_type_id: int) -> bool:
        """ลบประเภทตัวเลือก (soft delete)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ตรวจสอบว่ามี option values ที่ใช้ประเภทนี้อยู่หรือไม่
            cursor.execute('''
                SELECT ot.key FROM option_types ot
                WHERE ot.option_type_id = ?
            ''', (option_type_id,))
            
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False
            
            option_key = result['key']
            
            # ตรวจสอบว่ามี option values ที่ใช้ key นี้อยู่หรือไม่
            cursor.execute('''
                SELECT COUNT(*) as count FROM option_values 
                WHERE option_type = ? AND is_active = 1
            ''', (option_key,))
            
            if cursor.fetchone()['count'] > 0:
                # มี option values ที่ใช้อยู่ ไม่สามารถลบได้
                conn.close()
                return False
            
            # ลบประเภทตัวเลือก (soft delete)
            cursor.execute('''
                UPDATE option_types 
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE option_type_id = ?
            ''', (option_type_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting option type: {e}")
            return False