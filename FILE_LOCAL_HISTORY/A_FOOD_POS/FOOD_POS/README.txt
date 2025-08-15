========================================
           FOOD POS SYSTEM
========================================

ระบบจัดการร้านอาหารแบบครบวงจร
Complete Restaurant Management System

========================================
           QUICK START GUIDE
========================================

1. วิธีเริ่มต้นใช้งาน (How to Start):
   - ดับเบิลคลิก "Food_POS.bat" เพื่อเริ่มระบบ
   - ระบบจะเปิดเบราว์เซอร์อัตโนมัติ
   - หากไม่เปิดอัตโนมัติ ให้เปิดเบราว์เซอร์และไปที่: http://localhost:5000/admin

2. การติดตั้ง Python (ถ้าจำเป็น):
   - ดาวน์โหลดจาก: https://python.org
   - หรือติดตั้งจาก Microsoft Store (ค้นหา "Python")
   - เลือก "Add Python to PATH" ขณะติดตั้ง
   - รีสตาร์ทคอมพิวเตอร์หลังติดตั้งเสร็จ

========================================
              SYSTEM FEATURES
========================================

📊 DASHBOARD & ANALYTICS:
   - สรุปยอดขายรายวัน/เดือน/ปี
   - กราฟแสดงแนวโน้มการขาย
   - รายงานสินค้าขายดี
   - สถิติลูกค้าและการสั่งซื้อ

🍽️ MENU MANAGEMENT:
   - เพิ่ม/แก้ไข/ลบรายการอาหาร
   - จัดหมวดหมู่อาหาร
   - อัพโหลดรูปภาพสินค้า
   - กำหนดราคาและส่วนลด

📋 ORDER MANAGEMENT:
   - รับออเดอร์แบบ Real-time
   - ติดตามสถานะการทำอาหาร
   - พิมพ์ใบเสร็จ
   - จัดการคิวการสั่งซื้อ

👥 CUSTOMER MANAGEMENT:
   - ฐานข้อมูลลูกค้า
   - ประวัติการสั่งซื้อ
   - โปรแกรมสะสมแต้ม
   - ส่งโปรโมชั่น

💰 FINANCIAL MANAGEMENT:
   - บันทึกรายรับ-รายจ่าย
   - รายงานกำไร-ขาดทุน
   - ติดตามต้นทุนวัตถุดิบ
   - ระบบภาษี

📊 INVENTORY MANAGEMENT:
   - จัดการสต็อกวัตถุดิบ
   - แจ้งเตือนสินค้าใกล้หมด
   - บันทึกการรับ-จ่ายสินค้า
   - คำนวณต้นทุน

👨‍💼 STAFF MANAGEMENT:
   - จัดการข้อมูลพนักงาน
   - บันทึกเวลาทำงาน
   - คำนวณเงินเดือน
   - กำหนดสิทธิ์การใช้งาน

🎯 PROMOTION SYSTEM:
   - สร้างโปรโมชั่น
   - ระบบคูปอง
   - ส่วนลดตามเงื่อนไข
   - Happy Hour

========================================
              FILE STRUCTURE
========================================

FOOD_POS/
├── main.py                 # Main application file
├── Food_POS.bat           # System launcher
├── templates/             # HTML templates
│   ├── admin.html         # Admin dashboard
│   ├── menu.html          # Menu management
│   ├── orders.html        # Order management
│   ├── customers.html     # Customer management
│   ├── financial.html     # Financial reports
│   ├── inventory.html     # Inventory management
│   ├── staff.html         # Staff management
│   └── promotions.html    # Promotion management
├── static/                # Static files
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── images/           # Image files
├── data/                  # Data storage
│   ├── menu.json         # Menu data
│   ├── orders.json       # Order history
│   ├── customers.json    # Customer database
│   ├── financial.json    # Financial records
│   ├── inventory.json    # Inventory data
│   ├── staff.json        # Staff information
│   └── promotions.json   # Promotion data
└── logs/                  # System logs
    └── app.log           # Application log file

========================================
              TROUBLESHOOTING
========================================

❌ ปัญหา: ไม่สามารถเริ่มระบบได้
✅ แก้ไข:
   - ตรวจสอบว่าติดตั้ง Python แล้ว
   - รันในฐานะ Administrator
   - ปิดโปรแกรม Antivirus ชั่วคราว

❌ ปัญหา: เบราว์เซอร์ไม่เปิดอัตโนมัติ
✅ แก้ไข:
   - เปิดเบราว์เซอร์ด้วยตนเอง
   - ไปที่ http://localhost:5000/admin

❌ ปัญหา: ข้อมูลหายหลังปิดระบบ
✅ แก้ไข:
   - ตรวจสอบโฟลเดอร์ data/
   - ตรวจสอบสิทธิ์การเขียนไฟล์

========================================
              SUPPORT & CONTACT
========================================

หากมีปัญหาการใช้งาน:
1. ตรวจสอบไฟล์ logs/app.log
2. อ่านคู่มือนี้อีกครั้ง
3. ติดต่อผู้พัฒนาระบบ

เวอร์ชั่น: 1.0.0
พัฒนาโดย: AI Assistant
วันที่อัพเดต: 2024

========================================