# Google Sheets Complete Layout และข้อมูลทั้งหมด

## ภาพรวมระบบ Google Sheets Integration

ระบบ POS นี้มีการเชื่อมต่อกับ Google Sheets เพื่อบันทึกและวิเคราะห์ข้อมูลการขายอย่างครบถ้วน โดยมีการจัดเก็บข้อมูลใน 5 Sheet หลัก:

### 📊 **Sheet ทั้งหมดที่มีในระบบ:**
1. **Orders** - ข้อมูลออเดอร์หลัก
2. **Order_Items** - รายการสินค้าในแต่ละออเดอร์
3. **Daily_Summary** - สรุปยอดขายรายวัน
4. **Monthly_Summary** - สรุปยอดขายรายเดือน
5. **Item_Analytics** - วิเคราะห์ยอดขายสินค้า

---

## 📋 **1. Orders Sheet - ข้อมูลออเดอร์หลัก**

### โครงสร้างตาราง:
| คอลัมน์ | ชื่อฟิลด์ | ประเภทข้อมูล | คำอธิบาย |
|---------|-----------|--------------|----------|
| A | Order ID | Number | รหัสออเดอร์ (Auto increment) |
| B | Table Number | Number | หมายเลขโต๊ะ |
| C | Session ID | Text | รหัสเซสชั่น |
| D | Status | Text | สถานะ (รอดำเนินการ/กำลังเตรียม/พร้อมเสิร์ฟ/เสร็จสิ้น/ยกเลิก) |
| E | Total Amount (฿) | Currency | ยอดรวมเงิน |
| F | Payment Method | Text | วิธีการชำระเงิน |
| G | Customer Count | Number | จำนวนลูกค้า |
| H | Order Type | Text | ประเภทออเดอร์ |
| I | Created Date | Date | วันที่สร้างออเดอร์ |
| J | Created Time | Time | เวลาที่สร้างออเดอร์ |
| K | Completed Date | Date | วันที่เสร็จสิ้น |
| L | Completed Time | Time | เวลาที่เสร็จสิ้น |
| M | Duration (min) | Number | ระยะเวลาการให้บริการ (นาที) |
| N | Updated At | DateTime | เวลาอัปเดตล่าสุด |

### ตัวอย่างข้อมูล:
```
Order ID | Table | Session | Status    | Total | Payment | Customers | Type   | Created Date | Created Time | Completed Date | Completed Time | Duration | Updated At
171      | 1     | abc123  | เสร็จสิ้น | 869   | เงินสด  | 2         | Dine-in| 2025-01-10   | 10:30:00     | 2025-01-10     | 10:45:00       | 15       | 2025-01-10 10:45:30
```

---

## 🍽️ **2. Order_Items Sheet - รายการสินค้าในออเดอร์**

### โครงสร้างตาราง:
| คอลัมน์ | ชื่อฟิลด์ | ประเภทข้อมูล | คำอธิบาย |
|---------|-----------|--------------|----------|
| A | Order Item ID | Number | รหัสรายการสินค้า |
| B | Order ID | Number | รหัสออเดอร์ (เชื่อมโยงกับ Orders) |
| C | Item ID | Number | รหัสสินค้า |
| D | Category | Text | หมวดหมู่สินค้า |
| E | Item Name | Text | ชื่อสินค้า |
| F | Quantity | Number | จำนวน |
| G | Unit Price (฿) | Currency | ราคาต่อหน่วย |
| H | Total Price (฿) | Currency | ราคารวม |
| I | Discount (%) | Percentage | ส่วนลด |
| J | Final Price (฿) | Currency | ราคาสุดท้าย |
| K | Customer Request | Text | คำขอพิเศษจากลูกค้า |
| L | Special Options | Text | ตัวเลือกพิเศษ (เผ็ด, หวาน, เค็ม) |
| M | Status | Text | สถานะรายการ |
| N | Created At | DateTime | เวลาที่สร้าง |

### ตัวอย่างข้อมูล:
```
Item ID | Order ID | Item ID | Category  | Item Name        | Qty | Unit Price | Total | Discount | Final | Customer Request | Options      | Status | Created At
1       | 171      | 8       | เมนูข้าว  | ข้าวกะเพราทะเล   | 1   | 59.00      | 59.00 | 0%       | 59.00 | ไม่ใส่หอม        | เผ็ดน้อย     | เสร็จ  | 2025-01-10 10:30:15
2       | 171      | 6       | เมนูข้าว  | ข้าวกะเพราหมูสับ | 1   | 49.00      | 49.00 | 0%       | 49.00 |                  | เผ็ดปานกลาง  | เสร็จ  | 2025-01-10 10:30:20
```

---

## 📈 **3. Daily_Summary Sheet - สรุปยอดขายรายวัน**

### โครงสร้างตาราง:
| คอลัมน์ | ชื่อฟิลด์ | ประเภทข้อมูล | คำอธิบาย |
|---------|-----------|--------------|----------|
| A | Date | Date | วันที่ |
| B | Day of Week | Text | วันในสัปดาห์ |
| C | Total Orders | Number | จำนวนออเดอร์ทั้งหมด |
| D | Completed Orders | Number | จำนวนออเดอร์ที่เสร็จสิ้น |
| E | Cancelled Orders | Number | จำนวนออเดอร์ที่ยกเลิก |
| F | Total Revenue (฿) | Currency | รายได้รวม |
| G | Total Items Sold | Number | จำนวนสินค้าที่ขายได้ |
| H | Average Order Value (฿) | Currency | มูลค่าเฉลี่ยต่อออเดอร์ |
| I | Peak Hour | Text | ช่วงเวลาที่มีลูกค้ามากที่สุด |
| J | Most Popular Item | Text | สินค้าขายดีที่สุด |
| K | Total Tables Served | Number | จำนวนโต๊ะที่ให้บริการ |
| L | Average Service Time (min) | Number | เวลาเฉลี่ยในการให้บริการ |
| M | Updated At | DateTime | เวลาอัปเดตล่าสุด |

### ตัวอย่างข้อมูล:
```
Date       | Day    | Total Orders | Completed | Cancelled | Revenue | Items Sold | Avg Order | Peak Hour  | Popular Item     | Tables | Avg Time | Updated At
2025-01-10 | พฤหัส  | 25          | 23        | 2         | 2500.00 | 45         | 108.70    | 12:00-13:00| ข้าวผัดกุ้ง      | 15     | 18       | 2025-01-10 23:59:59
```

---

## 📅 **4. Monthly_Summary Sheet - สรุปยอดขายรายเดือน**

### โครงสร้างตาราง:
| คอลัมน์ | ชื่อฟิลด์ | ประเภทข้อมูล | คำอธิบาย |
|---------|-----------|--------------|----------|
| A | Month-Year | Text | เดือน-ปี (เช่น มกราคม 2025) |
| B | Total Orders | Number | จำนวนออเดอร์รวมทั้งเดือน |
| C | Total Revenue (฿) | Currency | รายได้รวมทั้งเดือน |
| D | Average Daily Revenue (฿) | Currency | รายได้เฉลี่ยต่อวัน |
| E | Best Day | Text | วันที่มียอดขายดีที่สุด |
| F | Worst Day | Text | วันที่มียอดขายต่ำที่สุด |
| G | Growth Rate (%) | Percentage | อัตราการเติบโต |
| H | Top 3 Items | Text | สินค้าขายดี 3 อันดับแรก |
| I | Updated At | DateTime | เวลาอัปเดตล่าสุด |

---

## 🏆 **5. Item_Analytics Sheet - วิเคราะห์ยอดขายสินค้า**

### โครงสร้างตาราง:
| คอลัมน์ | ชื่อฟิลด์ | ประเภทข้อมูล | คำอธิบาย |
|---------|-----------|--------------|----------|
| A | Item Name | Text | ชื่อสินค้า |
| B | Category | Text | หมวดหมู่ |
| C | Total Sold | Number | จำนวนที่ขายได้ทั้งหมด |
| D | Total Revenue (฿) | Currency | รายได้รวมจากสินค้านี้ |
| E | Average Price (฿) | Currency | ราคาเฉลี่ย |
| F | Popularity Rank | Number | อันดับความนิยม |
| G | Last Ordered | Date | วันที่สั่งล่าสุด |
| H | Frequency Score | Number | คะแนนความถี่ในการสั่ง |
| I | Profit Margin (%) | Percentage | อัตรากำไร |
| J | Updated At | DateTime | เวลาอัปเดตล่าสุด |

---

## ⚙️ **การตั้งค่าและคอนฟิกูเรชั่น**

### ไฟล์ google_sheets_config.json:
```json
{
  "enabled": true,
  "spreadsheet_id": "1QzitACA2BDNwsjYm8OvTRQORYDk6QDG3nKoM5OFSpJc",
  "sheet_names": {
    "orders": "Orders",
    "order_items": "Order_Items",
    "daily_summary": "Daily_Summary",
    "monthly_summary": "Monthly_Summary",
    "item_analytics": "Item_Analytics"
  },
  "features": {
    "auto_formatting": true,
    "daily_statistics": true,
    "item_analytics": true,
    "professional_layout": true,
    "thai_language": true
  }
}
```

### ฟีเจอร์ที่รองรับ:
- ✅ **Auto Formatting**: จัดรูปแบบตารางอัตโนมัติ
- ✅ **Daily Statistics**: สถิติรายวันแบบละเอียด
- ✅ **Item Analytics**: วิเคราะห์ยอดขายสินค้า
- ✅ **Professional Layout**: เลย์เอาต์แบบมืออาชีพ
- ✅ **Thai Language**: รองรับภาษาไทย

---

## 🎨 **การจัดรูปแบบ (Formatting)**

### หัวตาราง (Headers):
- **สีพื้นหลัง**: น้ำเงิน (#3399E6)
- **สีตัวอักษร**: ขาว
- **ฟอนต์**: ตัวหนา, ขนาด 11
- **การจัดตำแหน่ง**: กึ่งกลาง

### เซลล์ข้อมูล:
- **ตัวเลข**: จัดชิดขวา
- **ข้อความ**: จัดชิดซ้าย
- **วันที่**: รูปแบบ YYYY-MM-DD
- **เวลา**: รูปแบบ HH:MM:SS
- **เงิน**: รูปแบบ #,##0.00 ฿

---

## 🔄 **การซิงค์ข้อมูล**

### เมื่อไหร่ที่ข้อมูลจะถูกบันทึก:
1. **Orders & Order_Items**: เมื่อออเดอร์เสร็จสิ้น (Status = completed)
2. **Daily_Summary**: อัปเดตทุกวันเวลา 23:59
3. **Monthly_Summary**: อัปเดตทุกสิ้นเดือน
4. **Item_Analytics**: อัปเดตแบบ Real-time เมื่อมีการขาย

### ฟังก์ชันหลักที่ใช้:
- `sync_order()`: บันทึกข้อมูลออเดอร์
- `sync_order_items()`: บันทึกรายการสินค้า
- `sync_daily_summary()`: บันทึกสรุปรายวัน
- `update_item_analytics()`: อัปเดตสถิติสินค้า

---

## 📊 **ตัวอย่างข้อมูลจริงจากระบบ**

### จากภาพที่แนบมา (Order ID 171):
```
Order ID: 171
Table: 1
Items:
- ข้าวกะเพราทะเล (59฿)
- ข้าวกะเพราหมูสับ (49฿)
- ข้าวกะเพราไก่ (49฿)
- ข้าวปักใต้หอยลาย (49฿)
- ข้าวปักใต้ผัดพริกแกง (49฿)
- ชาลิ้ม (59฿)
- ชาลิ้ม (ความหวาน) (59฿)
- ข้าวกะเพราหมูสับ (เผ็ดมาก) (59฿)

Total: 869฿
Customer Requests: ไม่ใส่หอม, ไม่เผ็ด, ไม่เรียง
Special Options: ไม่ใส่ผัก, ไม่ใส่ผัก
```

---

## 🔧 **การแก้ไขปัญหา**

### ปัญหาที่พบบ่อย:
1. **ไม่สามารถเชื่อมต่อได้**
   - ตรวจสอบไฟล์ credentials.json
   - ตรวจสอบการแชร์ Google Sheets
   - ตรวจสอบ Google Sheets API

2. **ข้อมูลไม่อัปเดต**
   - ตรวจสอบ enabled = true ใน config
   - ตรวจสอบ spreadsheet_id
   - ตรวจสอบสิทธิ์การเขียน

3. **รูปแบบไม่ถูกต้อง**
   - เรียกใช้ format_headers() ใหม่
   - ตรวจสอบ auto_formatting = true

---

## 📱 **การเข้าถึงข้อมูล**

### URL Google Sheets:
```
https://docs.google.com/spreadsheets/d/1QzitACA2BDNwsjYm8OvTRQORYDk6QDG3nKoM5OFSpJc/edit
```

### การใช้งาน:
- เข้าถึงได้จากทุกที่ที่มีอินเทอร์เน็ต
- สามารถแชร์กับทีมงาน
- ใช้สำหรับการวิเคราะห์และรายงาน
- สำรองข้อมูลอัตโนมัติ

---

## 🚀 **การพัฒนาเพิ่มเติม**

### ฟีเจอร์ที่สามารถเพิ่มได้:
1. **Charts & Graphs**: กราฟแสดงยอดขาย
2. **Pivot Tables**: ตารางสรุปแบบไดนามิก
3. **Conditional Formatting**: เปลี่ยนสีตามเงื่อนไข
4. **Data Validation**: ตรวจสอบความถูกต้องของข้อมูล
5. **Automated Reports**: รายงานอัตโนมัติ

### การขยายระบบ:
- เพิ่ม Sheet สำหรับข้อมูลลูกค้า
- เพิ่ม Sheet สำหรับการจัดการสต็อก
- เพิ่ม Sheet สำหรับการวิเคราะห์พนักงาน
- เชื่อมต่อกับระบบบัญชี

นี่คือข้อมูลทั้งหมดของระบบ Google Sheets Integration ที่มีอยู่ในโปรเจกต์ POS ของคุณ 🎯