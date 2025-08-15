import sqlite3

conn = sqlite3.connect('pos_database.db')
cursor = conn.cursor()

# อัปเดตราคาของตัวเลือกพิเศษ
update_data = [
    ('ไข่ดาว', 10),
    ('ไข่เจียว', 20),
    ('เพิ่มข้าว', 10),
    ('ไม่เพิ่ม', 0)
]

print('กำลังอัปเดตราคาตัวเลือกพิเศษ...')

for name, price in update_data:
    cursor.execute('''
        UPDATE option_values 
        SET additional_price = ?
        WHERE option_type = "addon" AND name = ?
    ''', (price, name))
    
    # ตรวจสอบว่าอัปเดตสำเร็จหรือไม่
    if cursor.rowcount > 0:
        print(f'✓ อัปเดต {name} เป็น +{price}฿ สำเร็จ')
    else:
        print(f'✗ ไม่พบตัวเลือก {name} ในฐานข้อมูล')

conn.commit()

# ตรวจสอบผลลัพธ์
print('\nตรวจสอบราคาหลังอัปเดต:')
cursor.execute('SELECT name, additional_price FROM option_values WHERE option_type = "addon"')
results = cursor.fetchall()

for name, price in results:
    print(f'{name}: +{price}฿')

conn.close()
print('\nอัปเดตเสร็จสิ้น!')