@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                📦 FOOD POS SYSTEM INSTALLER 📦               ║
echo ║                  ติดตั้งระบบ POS สำหรับร้านอาหาร              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
echo 🔍 กำลังตรวจสอบ Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ไม่พบ Python ในระบบ
    echo.
    echo 📋 วิธีติดตั้ง Python:
    echo    1. ไปที่ https://python.org/downloads/
    echo    2. ดาวน์โหลด Python เวอร์ชันล่าสุด
    echo    3. รันไฟล์ติดตั้งและเลือก "Add Python to PATH"
    echo    4. รีสตาร์ทคอมพิวเตอร์หลังติดตั้งเสร็จ
    echo    5. รันไฟล์นี้อีกครั้ง
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ พบ Python %PYTHON_VERSION%
echo.

REM Check pip
echo 🔍 กำลังตรวจสอบ pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ไม่พบ pip
    echo 📦 กำลังติดตั้ง pip...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo ❌ ติดตั้ง pip ไม่สำเร็จ
        pause
        exit /b 1
    )
)
echo ✅ pip พร้อมใช้งาน
echo.

REM Upgrade pip
echo 🔄 กำลังอัปเดต pip...
python -m pip install --upgrade pip
echo.

REM Install requirements
echo 📦 กำลังติดตั้ง Python packages...
echo    (อาจใช้เวลาสักครู่)
echo.
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ❌ ติดตั้ง packages ไม่สำเร็จ
    echo.
    echo 🔧 วิธีแก้ไขปัญหา:
    echo    1. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
    echo    2. รันคำสั่งนี้ใน Command Prompt:
    echo       pip install --upgrade pip
    echo       pip install -r requirements.txt
    echo    3. หากยังไม่ได้ ลองติดตั้งทีละ package:
    echo       pip install Flask Flask-CORS qrcode[pil] Pillow
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ ติดตั้งเสร็จสมบูรณ์!
echo.
echo 🎉 ระบบ Food POS พร้อมใช้งานแล้ว
echo.
echo 📋 ขั้นตอนถัดไป:
echo    1. ดับเบิลคลิกไฟล์ "run.bat" เพื่อเริ่มต้นระบบ
echo    2. เปิดเว็บเบราว์เซอร์ไปที่ http://localhost:5000/admin.html
echo    3. ตั้งค่าระบบตามต้องการ
echo.
echo 📖 อ่านคู่มือเพิ่มเติมในไฟล์ README.md
echo.
pause