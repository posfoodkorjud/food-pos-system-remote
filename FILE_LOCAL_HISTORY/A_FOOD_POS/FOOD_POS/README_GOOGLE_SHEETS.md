# ฟีเจอร์ Google Sheets Integration

## ภาพรวม
ระบบ POS นี้สามารถบันทึกข้อมูลการขายลง Google Sheets ได้อัตโนมัติ เพื่อให้สามารถเข้าถึงข้อมูลจากที่ไหนก็ได้และสร้างรายงานได้ง่าย

## ฟีเจอร์ที่รองรับ
- ✅ บันทึกข้อมูลออเดอร์เมื่อเสร็จสิ้น
- ✅ บันทึกรายการสินค้าในแต่ละออเดอร์
- ✅ สรุปยอดขายรายวัน
- ✅ สร้างหัวตารางอัตโนมัติ
- ✅ ทดสอบการเชื่อมต่อ
- ✅ เปิด/ปิดการใช้งานได้

## ไฟล์ที่เกี่ยวข้อง

### Backend Files
- `backend/google_sheets.py` - โมดูลหลักสำหรับจัดการ Google Sheets
- `backend/database.py` - เพิ่มการเรียกใช้ Google Sheets เมื่อออเดอร์เสร็จสิ้น
- `backend/app.py` - API endpoints สำหรับการตั้งค่า

### Frontend Files
- `templates/admin.html` - หน้าตั้งค่า Google Sheets
- `backend/admin.js` - JavaScript สำหรับจัดการการตั้งค่า

### Configuration Files
- `google_sheets_config.json` - ไฟล์การตั้งค่า (สร้างอัตโนมัติ)
- `credentials.json` - ไฟล์ credentials จาก Google Cloud
- `google_sheets_config.example.json` - ตัวอย่างไฟล์การตั้งค่า

### Documentation
- `google_sheets_setup_guide.md` - คู่มือการตั้งค่าแบบละเอียด
- `README_GOOGLE_SHEETS.md` - ไฟล์นี้

## วิธีการใช้งาน

### 1. การตั้งค่าครั้งแรก
1. อ่านคู่มือใน `google_sheets_setup_guide.md`
2. สร้าง Google Cloud Project และ Service Account
3. ดาวน์โหลดไฟล์ credentials.json
4. สร้าง Google Sheets และแชร์กับ Service Account

### 2. การตั้งค่าในระบบ
1. เข้าหน้า Admin: `http://localhost:5000/admin`
2. ไปที่แท็บ "ตั้งค่าระบบ"
3. ในส่วน "Google Sheets Settings":
   - ใส่ Sheet ID
   - ใส่ชื่อชีท
   - อัปโหลดไฟล์ credentials.json
4. คลิก "บันทึก"
5. คลิก "ทดสอบ" เพื่อตรวจสอบการเชื่อมต่อ

### 3. การใช้งาน
- ข้อมูลจะถูกบันทึกอัตโนมัติเมื่อออเดอร์เสร็จสิ้น
- ตรวจสอบข้อมูลใน Google Sheets ที่ตั้งค่าไว้

## โครงสร้างข้อมูลใน Google Sheets

### Sheet: Orders
| Order ID | Table Number | Total Amount | Status | Created At | Completed At |
|----------|--------------|--------------|--------|------------|-------------|
| 1 | 5 | 350.00 | completed | 2025-01-10 10:30:00 | 2025-01-10 10:45:00 |

### Sheet: Order_Items
| Order ID | Item Name | Quantity | Price | Total | Options |
|----------|-----------|----------|-------|-------|--------|
| 1 | กะเพราหมู | 1 | 50.00 | 50.00 | เผ็ดน้อย, ไข่ดาว |

### Sheet: Daily_Summary
| Date | Total Orders | Total Amount | Average Order Value |
|------|--------------|--------------|--------------------|
| 2025-01-10 | 25 | 8750.00 | 350.00 |

## การแก้ไขปัญหา

### ตรวจสอบสถานะ
```python
# ตรวจสอบว่าเปิดใช้งาน Google Sheets หรือไม่
from backend.google_sheets import is_google_sheets_enabled
print(is_google_sheets_enabled())
```

### ข้อผิดพลาดที่พบบ่อย
1. **ไม่สามารถเชื่อมต่อได้**
   - ตรวจสอบไฟล์ credentials.json
   - ตรวจสอบการแชร์ชีท
   - ตรวจสอบ Google Sheets API

2. **ไม่มีสิทธิ์เขียน**
   - ตรวจสอบสิทธิ์ของ Service Account
   - ตรวจสอบการป้องกันชีท

3. **Sheet ID ผิด**
   - ตรวจสอบ URL ของ Google Sheets
   - คัดลอก ID ใหม่

## การปรับแต่ง

### เปลี่ยนชื่อชีทย่อย
แก้ไขในไฟล์ `google_sheets_config.json`:
```json
{
  "sheets": {
    "orders": "ออเดอร์",
    "order_items": "รายการสินค้า",
    "daily_summary": "สรุปรายวัน"
  }
}
```

### เปลี่ยนหัวตาราง
แก้ไขในไฟล์ `google_sheets_config.json`:
```json
{
  "headers": {
    "orders": ["รหัสออเดอร์", "โต๊ะ", "ยอดรวม", "สถานะ", "สร้างเมื่อ", "เสร็จเมื่อ"]
  }
}
```

### ปิดการใช้งาน
แก้ไขในไฟล์ `google_sheets_config.json`:
```json
{
  "enabled": false
}
```

## การพัฒนาเพิ่มเติม

### เพิ่มข้อมูลใหม่
1. แก้ไขฟังก์ชัน `sync_order_to_sheets` ใน `backend/google_sheets.py`
2. เพิ่มหัวตารางใน config
3. ทดสอบการทำงาน

### เพิ่ม Sheet ใหม่
1. เพิ่มชื่อ sheet ใน config
2. สร้างฟังก์ชันสำหรับ sync ข้อมูล
3. เรียกใช้ในจุดที่เหมาะสม

## การสำรองข้อมูล
- ข้อมูลใน Google Sheets เป็นการสำรองข้อมูลเพิ่มเติม
- ข้อมูลหลักยังคงอยู่ในฐานข้อมูล SQLite
- สามารถใช้ Google Sheets สำหรับการวิเคราะห์และรายงาน

## ความปลอดภัย
- ไฟล์ credentials.json ควรเก็บไว้อย่างปลอดภัย
- ไม่ควร commit ไฟล์ credentials.json ลง Git
- ใช้ Service Account แทนการใช้ Personal Account
- ตั้งสิทธิ์ให้เหมาะสมในการแชร์ชีท