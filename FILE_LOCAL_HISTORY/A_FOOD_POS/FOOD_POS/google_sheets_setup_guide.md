# คู่มือการตั้งค่า Google Sheets สำหรับระบบ POS

## ขั้นตอนการตั้งค่า

### 1. สร้าง Google Sheets
1. เข้าไปที่ [Google Sheets](https://sheets.google.com)
2. สร้างชีทใหม่
3. ตั้งชื่อชีท เช่น "ยอดขาย POS"
4. คัดลอก ID ของชีทจาก URL
   - URL จะมีรูปแบบ: `https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit`
   - คัดลอกส่วน `[SHEET_ID]`

### 2. สร้าง Google Cloud Project และ Service Account
1. เข้าไปที่ [Google Cloud Console](https://console.cloud.google.com)
2. สร้างโปรเจกต์ใหม่หรือเลือกโปรเจกต์ที่มีอยู่
3. เปิดใช้งาน Google Sheets API:
   - ไปที่ "APIs & Services" > "Library"
   - ค้นหา "Google Sheets API"
   - คลิก "Enable"

4. สร้าง Service Account:
   - ไปที่ "APIs & Services" > "Credentials"
   - คลิก "Create Credentials" > "Service Account"
   - ตั้งชื่อ Service Account
   - คลิก "Create and Continue"
   - เลือก Role: "Editor" หรือ "Owner"
   - คลิก "Done"

5. สร้าง Key สำหรับ Service Account:
   - คลิกที่ Service Account ที่สร้างไว้
   - ไปที่แท็บ "Keys"
   - คลิก "Add Key" > "Create new key"
   - เลือก "JSON"
   - ดาวน์โหลดไฟล์ JSON (นี่คือไฟล์ credentials.json)

### 3. แชร์ Google Sheets กับ Service Account
1. เปิดไฟล์ credentials.json ที่ดาวน์โหลดมา
2. หา email ของ Service Account (จะมีรูปแบบ: `xxx@xxx.iam.gserviceaccount.com`)
3. กลับไปที่ Google Sheets ที่สร้างไว้
4. คลิก "Share" (แชร์)
5. ใส่ email ของ Service Account
6. ตั้งสิทธิ์เป็น "Editor"
7. คลิก "Send"

### 4. ตั้งค่าในระบบ POS
1. เข้าไปที่หน้า Admin ของระบบ POS
2. ไปที่แท็บ "ตั้งค่าระบบ"
3. ในส่วน "Google Sheets Settings":
   - **Sheet ID**: ใส่ ID ของ Google Sheets ที่คัดลอกมา
   - **Sheet Name**: ใส่ชื่อชีท (เช่น "ยอดขาย")
   - **Credentials File**: อัปโหลดไฟล์ credentials.json
4. คลิก "บันทึก"
5. คลิก "ทดสอบ" เพื่อตรวจสอบการเชื่อมต่อ

## โครงสร้างข้อมูลที่จะบันทึกใน Google Sheets

ระบบจะสร้างชีทย่อย 3 ชีท:

### 1. Orders (ข้อมูลออเดอร์)
- Order ID
- Table Number
- Total Amount
- Status
- Created At
- Completed At

### 2. Order_Items (รายการสินค้าในออเดอร์)
- Order ID
- Item Name
- Quantity
- Price
- Total
- Options

### 3. Daily_Summary (สรุปยอดขายรายวัน)
- Date
- Total Orders
- Total Amount
- Average Order Value

## การแก้ไขปัญหา

### ข้อผิดพลาดที่พบบ่อย
1. **"ไม่สามารถเชื่อมต่อ Google Sheets ได้"**
   - ตรวจสอบว่าไฟล์ credentials.json ถูกต้อง
   - ตรวจสอบว่าได้แชร์ชีทกับ Service Account แล้ว
   - ตรวจสอบว่า Google Sheets API เปิดใช้งานแล้ว

2. **"Sheet ID ไม่ถูกต้อง"**
   - ตรวจสอบ Sheet ID ที่คัดลอกมาจาก URL
   - ตรวจสอบว่าชีทเป็น Public หรือแชร์กับ Service Account แล้ว

3. **"ไม่มีสิทธิ์เขียนข้อมูล"**
   - ตรวจสอบว่า Service Account มีสิทธิ์ Editor ในชีท
   - ตรวจสอบว่าชีทไม่ได้ถูกป้องกันการแก้ไข

## หมายเหตุ
- ข้อมูลจะถูกบันทึกลง Google Sheets เมื่อออเดอร์เสร็จสิ้น (Complete)
- ระบบจะสร้างหัวตารางอัตโนมัติในครั้งแรกที่ใช้งาน
- ข้อมูลจะถูกเพิ่มต่อท้ายในแต่ละชีท
- สามารถปิด/เปิดการบันทึกข้อมูลได้ในไฟล์ config