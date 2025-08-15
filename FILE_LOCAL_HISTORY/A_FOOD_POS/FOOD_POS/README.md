# 🍽️ Food POS System - ระบบ POS สำหรับร้านอาหาร

> ระบบ Point of Sale (POS) สำหรับร้านอาหารแบบครบวงจร พร้อมระบบสั่งอาหารผ่าน QR Code, การชำระเงินผ่าน PromptPay และการบันทึกยอดขายใน Google Sheets

## ✨ คุณสมบัติหลัก

### 🖥️ ฝั่งร้าน (Admin Panel)
- 📊 **จัดการโต๊ะ**: เพิ่ม/ลบโต๊ะ, สร้าง QR Code, ดูสถานะโต๊ะ
- 🍜 **จัดการเมนู**: แบ่งหมวดหมู่, เพิ่ม/แก้ไข/ลบเมนู
- 📋 **รับออเดอร์**: แสดงรายการสั่งอาหารแบบเรียลไทม์
- 🧾 **เช็คบิล**: สรุปยอด, พิมพ์ใบเสร็จพร้อม QR PromptPay
- ⚙️ **การตั้งค่า**: PromptPay, Google Sheets, Domain

### 📱 ฝั่งลูกค้า (Customer Web App)
- 🔍 **เลือกเมนู**: แสดงตามหมวดหมู่พร้อมรูปภาพและราคา
- 🛒 **สั่งอาหาร**: เพิ่มจำนวน, ยืนยันคำสั่งซื้อ
- 📝 **ดูรายการ**: รวมทุกเมนูที่สั่งและยอดรวม
- 🔔 **เรียกพนักงาน**: ส่งสัญญาณไปยังฝั่งร้าน
- 💰 **เช็คบิล**: ขอใบเสร็จและปิด session

### 🔧 ระบบเสริม
- 💳 **PromptPay**: สร้าง QR Code รับเงินอัตโนมัติ
- 📊 **Google Sheets**: บันทึกยอดขายแบบเรียลไทม์
- 🖨️ **พิมพ์ใบเสร็จ**: รองรับเครื่องพิมพ์ความร้อน (ตัวเลือก)

## 🏗️ สถาปัตยกรรมระบบ

- **ฝั่งลูกค้า**: Web App (HTML/CSS/JS + Bootstrap)
- **ฝั่งร้าน**: Web-based Admin Panel
- **Backend**: Python Flask Server
- **ฐานข้อมูล**: SQLite (Local)
- **การชำระเงิน**: PromptPay QR Code
- **บันทึกยอดขาย**: Google Sheets API

## 📁 โครงสร้างโปรเจค

```
FOOD_POS/
├── main.py                 # ไฟล์หลักสำหรับเริ่มต้นระบบ
├── requirements.txt        # รายการ Python packages
├── README.md              # คู่มือการใช้งาน
├── backend/               # ระบบหลังบ้าน
│   ├── __init__.py
│   ├── app.py            # Flask web server
│   ├── database.py       # จัดการฐานข้อมูล SQLite
│   ├── models.py         # โมเดลข้อมูล
│   └── utils/            # เครื่องมือเสริม
│       ├── __init__.py
│       ├── qr_generator.py    # สร้าง QR Code
│       ├── promptpay.py       # PromptPay QR Code
│       └── google_sheets.py   # Google Sheets API
└── frontend/              # ส่วนหน้าเว็บ
    ├── index.html        # หน้าหลักลูกค้า
    ├── order.html        # หน้าสั่งอาหาร
    ├── admin.html        # หน้า Admin Panel
    ├── css/              # ไฟล์ CSS
    │   ├── order.css
    │   └── admin.css
    └── js/               # ไฟล์ JavaScript
        └── admin.js
```

## 🚀 การติดตั้งและใช้งาน

### ข้อกำหนดระบบ
- **ระบบปฏิบัติการ**: Windows 10/11
- **Python**: 3.8 หรือใหม่กว่า
- **เน็ตอินเทอร์เน็ต**: สำหรับ Google Sheets และลูกค้าใช้งาน

### 📦 ขั้นตอนการติดตั้ง

#### 1. ติดตั้ง Python
```bash
# ดาวน์โหลดและติดตั้ง Python จาก https://python.org
# ตรวจสอบการติดตั้ง
python --version
pip --version
```

#### 2. ติดตั้ง Dependencies
```bash
# เปิด Command Prompt หรือ PowerShell
cd C:\Users\gumun\Desktop\FOOD_POS

# ติดตั้ง packages ที่จำเป็น
pip install -r requirements.txt
```

#### 3. เริ่มต้นระบบ
```bash
# รันระบบ
python main.py
```

### 3. การตั้งค่า
- ตั้งค่า PromptPay (เบอร์โทร/เลขบัตรประชาชน)
- เชื่อมต่อ Google Sheets
- กำหนดโดเมนสำหรับ Web App

## ✨ ฟีเจอร์หลัก

### ฝั่งร้าน (Desktop App)
- 🏪 จัดการโต๊ะและสร้าง QR Code
- 🍜 จัดการเมนูอาหารและราคา
- 📋 รับและติดตามออเดอร์
- 🧾 พิมพ์ใบเสร็จพร้อม PromptPay
- 📊 ส่งข้อมูลยอดขายไป Google Sheets

### ฝั่งลูกค้า (Web App)
- 📱 สแกน QR Code เพื่อเข้าสู่ระบบ
- 🍽️ เลือกและสั่งอาหาร
- 👋 เรียกพนักงาน
- 💰 เช็คบิลและชำระเงิน

## 🔧 เทคโนโลยีที่ใช้

- **Backend**: Python, Flask, SQLite
- **Desktop**: PyQt5
- **Frontend**: HTML5, CSS3, JavaScript, Vue.js, Bootstrap
- **Payment**: PromptPay QR Code
- **Integration**: Google Sheets API
- **QR Code**: Python qrcode library

## 📞 การสนับสนุน

สำหรับคำถามหรือปัญหาการใช้งาน กรุณาติดต่อทีมพัฒนา