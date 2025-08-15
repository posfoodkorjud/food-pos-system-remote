# 🛠️ เครื่องมือป้องกันปัญหา Database Schema

## 📁 ไฟล์ที่สร้างขึ้น

### 1. `database_consistency_check.py`
**วัตถุประสงค์:** ตรวจสอบความสอดคล้องระหว่างฐานข้อมูลและโค้ด

**การใช้งาน:**
```bash
python database_consistency_check.py
```

**ฟีเจอร์:**
- ตรวจสอบโครงสร้างตาราง order_items
- ค้นหา special_request ที่เหลืออยู่ในโค้ด
- สร้างรายงานปัญหาที่พบ
- สร้างสคริปต์แก้ไขอัตโนมัติ

### 2. `PREVENTION_GUIDE.md`
**วัตถุประสงค์:** คู่มือป้องกันปัญหาในอนาคต

**เนื้อหา:**
- ขั้นตอนการเปลี่ยนแปลง schema อย่างปลอดภัย
- เครื่องมือและสคริปต์ช่วยเหลือ
- Naming conventions
- Emergency recovery procedures
- Checklist สำหรับการเปลี่ยนแปลง

### 3. `quick_fix.bat`
**วัตถุประสงค์:** เครื่องมือ GUI แบบ command-line สำหรับการแก้ไขด่วน

**การใช้งาน:**
```bash
quick_fix.bat
```

**ฟีเจอร์:**
- ตรวจสอบความสอดคล้อง
- แก้ไขอัตโนมัติ
- ทดสอบ API
- สำรองฐานข้อมูล
- เมนูใช้งานง่าย

## 🚀 วิธีใช้งานเบื้องต้น

### สำหรับการตรวจสอบประจำ
```bash
# วิธีที่ 1: ใช้สคริปต์ Python
python database_consistency_check.py

# วิธีที่ 2: ใช้ Quick Fix Tool
quick_fix.bat
# เลือกตัวเลือก 1 (ตรวจสอบความสอดคล้อง)
```

### สำหรับการแก้ไขปัญหา
```bash
# วิธีที่ 1: ใช้ Quick Fix Tool (แนะนำ)
quick_fix.bat
# เลือกตัวเลือก 4 (สำรองฐานข้อมูล) ก่อน
# จากนั้นเลือกตัวเลือก 2 (แก้ไขอัตโนมัติ)

# วิธีที่ 2: ใช้สคริปต์ที่สร้างอัตโนมัติ
python database_consistency_check.py  # สร้างไฟล์ fix_special_request.py
python fix_special_request.py          # รันการแก้ไข
```

### สำหรับการทดสอบหลังแก้ไข
```bash
# ทดสอบผ่าน Quick Fix Tool
quick_fix.bat
# เลือกตัวเลือก 3 (ทดสอบ API)

# หรือทดสอบด้วยตนเอง
curl -X GET http://localhost:5000/api/orders
```

## ⚡ Quick Reference

### ปัญหาที่พบบ่อย
| ปัญหา | สาเหตุ | วิธีแก้ |
|-------|--------|--------|
| HTTP 500 "no such column" | ชื่อคอลัมน์ไม่ตรงกัน | รัน quick_fix.bat → ตัวเลือก 2 |
| special_request ใน error log | โค้ดยังใช้ชื่อเก่า | ตรวจสอบด้วย database_consistency_check.py |
| API ไม่ส่งข้อมูล customer_request | Schema ไม่สอดคล้อง | อ่าน PREVENTION_GUIDE.md |

### คำสั่งด่วน
```bash
# ตรวจสอบปัญหา
python database_consistency_check.py

# สำรองก่อนแก้ไข
cp pos_database.db pos_database_backup_$(date +%Y%m%d_%H%M%S).db

# ทดสอบ API
curl -X GET http://localhost:5000/api/orders
```

## 📋 Maintenance Schedule

### รายสัปดาห์
- [ ] รัน `database_consistency_check.py`
- [ ] ตรวจสอบ error logs
- [ ] ทดสอบ API endpoints หลัก

### ก่อนการ Deploy
- [ ] รัน `quick_fix.bat` → ตรวจสอบความสอดคล้อง
- [ ] สำรองฐานข้อมูล
- [ ] ทดสอบ API ทั้งหมด
- [ ] ตรวจสอบ error logs

### หลังการเปลี่ยนแปลง Schema
- [ ] รัน consistency check ทันที
- [ ] ทดสอบ API ที่เกี่ยวข้อง
- [ ] อัปเดต documentation
- [ ] สร้าง backup point

## 🆘 Emergency Contacts

หากเครื่องมือเหล่านี้ไม่สามารถแก้ปัญหาได้:

1. **ตรวจสอบ error logs ใน terminal**
2. **อ่าน PREVENTION_GUIDE.md ส่วน Emergency Recovery**
3. **กู้คืนจาก backup ล่าสุด**
4. **ติดต่อทีมพัฒนา**

---

**📝 หมายเหตุ:** เครื่องมือเหล่านี้ออกแบบมาเพื่อป้องกันปัญหา special_request/customer_request โดยเฉพาะ แต่สามารถปรับใช้กับปัญหา schema อื่นๆ ได้