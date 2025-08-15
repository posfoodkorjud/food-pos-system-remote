@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🍽️  FOOD POS SYSTEM  🍽️                    ║
echo ║                  ระบบ POS สำหรับร้านอาหาร                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🔍 กำลังตรวจสอบ Python...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ไม่พบ Python ในระบบ
    echo 📦 กรุณาติดตั้ง Python จาก https://python.org
    echo    - เลือก "Add Python to PATH" ขณะติดตั้ง
    echo    - รีสตาร์ทคอมพิวเตอร์หลังติดตั้งเสร็จ
    echo.
    pause
    exit /b 1
)

echo ✅ พบ Python แล้ว
echo.
echo 📦 กำลังตรวจสอบ dependencies...

REM Check if requirements are installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  กำลังติดตั้ง dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ ติดตั้ง dependencies ไม่สำเร็จ
        echo 🔧 ลองรันคำสั่งนี้ใน Command Prompt:
        echo    pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo ✅ Dependencies พร้อมใช้งาน
echo.
echo 🚀 กำลังเริ่มต้นระบบ...
echo.
echo 📋 ข้อมูลการเข้าถึง:
echo    📊 Admin Panel:     http://localhost:5000/admin.html
echo    📱 Customer App:    http://localhost:5000/
echo    🔧 API Endpoint:    http://localhost:5000/api/
echo.
echo ⚠️  กด Ctrl+C เพื่อหยุดระบบ
echo ═══════════════════════════════════════════════════════════════
echo.

REM Start the application
python main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ เกิดข้อผิดพลาดในการเริ่มต้นระบบ
    echo 🔧 ตรวจสอบ error message ด้านบนและแก้ไขปัญหา
    echo.
    pause
)