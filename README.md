# POS KORJUD - Point of Sale System

## ระบบจุดขายออนไลน์สำหรับร้านอาหาร KORJUD

### 📋 ข้อมูลเมนูปัจจุบัน
- **จำนวนเมนูทั้งหมด**: 77 รายการ
- **เมนูน้ำ**: 34 รายการ
- **เมนูข้าว**: 28 รายการ  
- **เมนูเส้น**: 9 รายการ
- **เมนูน้ำปั่น**: 6 รายการ

### 🔄 การอัปเดตล่าสุด
- ลบเมนูซ้ำ 17 รายการ
- ลบเมนูที่ไม่เหมาะสม 5 รายการ
- ทำความสะอาดฐานข้อมูลเมนูให้เหลือ 77 รายการที่พร้อมใช้งาน
- อัปเดต configuration สำหรับ production deployment

### 🚀 การ Deploy

#### Local Development
```bash
cd A_FOOD_POS/FOOD_POS
python main.py
```

#### Production (Render)
- URL: https://food-pos-system.onrender.com
- Auto-deploy จาก Git repository
- ใช้ PostgreSQL สำหรับ production database

### 📁 โครงสร้างโปรเจค
```
POS_KORJUD/
├── A_FOOD_POS/FOOD_POS/          # Main application
│   ├── backend/                   # Backend API
│   ├── frontend/                  # Frontend files
│   ├── main.py                    # Application entry point
│   └── requirements.txt           # Python dependencies
├── pos_database.db               # Local SQLite database
└── README.md                     # This file
```

### 🛠️ Features
- ระบบจัดการโต๊ะและออเดอร์
- QR Code สำหรับการสั่งอาหาร
- Admin Panel สำหรับจัดการเมนูและยอดขาย
- รองรับ PromptPay และ Google Sheets integration
- Responsive design สำหรับมือถือและเดสก์ท็อป

### 📊 Database Schema
- **menus**: ข้อมูลเมนูอาหาร (77 รายการ)
- **orders**: ข้อมูลออเดอร์
- **tables**: ข้อมูลโต๊ะ
- **order_items**: รายการสินค้าในออเดอร์

### 🔧 การอัปเดตเมนู
หากต้องการอัปเดตเมนูใหม่:
1. แก้ไขข้อมูลในฐานข้อมูล
2. Commit และ Push ไปยัง Git
3. Render จะ auto-deploy อัตโนมัติ

### 📝 Git History
- `c2eef92`: Update menu database - Clean up duplicates and reduce to 77 items
- `e7a7088`: Initial commit - POS System ready for deployment

---

**สถานะ**: ✅ พร้อมใช้งาน - เมนู 77 รายการได้รับการยืนยันและทำความสะอาดแล้ว