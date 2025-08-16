# Full POS System

ระบบ Point of Sale (POS) สำหรับร้านอาหาร ที่ได้รับการจัดระเบียบและปรับปรุงแล้ว

## โครงสร้างระบบ

```
Full_POS/
├── backend/                    # ระบบ Backend (Flask API)
├── frontend/                   # ระบบ Frontend (HTML/CSS/JS)
├── menu_backups/              # โฟลเดอร์สำหรับ backup เมนู
├── pos_database.db            # ฐานข้อมูลหลัก (77 รายการเมนู, 4 หมวดหมู่)
├── requirements.txt           # รายการ Python packages ที่จำเป็น
├── create_menu_backup.py      # สร้าง backup เมนู
├── menu_health_check.py       # ตรวจสอบสุขภาพเมนู
├── auto_menu_recovery.py      # กู้คืนเมนูอัตโนมัติ
├── restore_menu_backup.py     # กู้คืนเมนูด้วยตนเอง
├── MENU_PROTECTION_GUIDE.md   # คู่มือการใช้งานเครื่องมือป้องกันเมนู
└── README.md                  # ไฟล์นี้
```

## การติดตั้งและใช้งาน

### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 2. เริ่มต้นระบบ
```bash
python backend/app.py
```

### 3. เข้าใช้งานระบบ
เปิดเว็บเบราว์เซอร์และไปที่: `http://localhost:5000`

## ข้อมูลเมนูปัจจุบัน

- **จำนวนหมวดหมู่**: 4 หมวดหมู่
- **จำนวนรายการเมนู**: 77 รายการ
- **ช่วงราคา**: 29-59 บาท
- **สถานะ**: ข้อมูลสะอาด ไม่มีรายการซ้ำ

## เครื่องมือจัดการเมนู

### การสร้าง Backup
```bash
python create_menu_backup.py
```

### การตรวจสอบสุขภาพเมนู
```bash
python menu_health_check.py
```

### การกู้คืนอัตโนมัติ
```bash
python auto_menu_recovery.py
```

### การกู้คืนด้วยตนเอง
```bash
python restore_menu_backup.py
```

## คำแนะนำการใช้งาน

1. **สร้าง Backup เป็นประจำ**: ใช้ `create_menu_backup.py` เพื่อสร้าง backup ก่อนทำการเปลี่ยนแปลงใดๆ
2. **ตรวจสอบสุขภาพเมนู**: ใช้ `menu_health_check.py` เพื่อตรวจสอบความถูกต้องของข้อมูลเมนู
3. **กู้คืนเมื่อจำเป็น**: หากเกิดปัญหา ใช้ `auto_menu_recovery.py` หรือ `restore_menu_backup.py`

## หมายเหตุสำคัญ

- ระบบนี้ได้รับการทำความสะอาดและจัดระเบียบแล้ว
- ข้อมูลเมนูอยู่ในสภาพที่ถูกต้องและพร้อมใช้งาน
- มีระบบ backup และ recovery ที่สมบูรณ์
- สำหรับข้อมูลเพิ่มเติมเกี่ยวกับการป้องกันและกู้คืนเมนู ดูที่ `MENU_PROTECTION_GUIDE.md`

## การสนับสนุน

หากพบปัญหาหรือต้องการความช่วยเหลือ:
1. ตรวจสอบ `MENU_PROTECTION_GUIDE.md` สำหรับคำแนะนำโดยละเอียด
2. ใช้เครื่องมือ `menu_health_check.py` เพื่อวินิจฉัยปัญหา
3. ใช้ `auto_menu_recovery.py` เพื่อแก้ไขปัญหาอัตโนมัติ