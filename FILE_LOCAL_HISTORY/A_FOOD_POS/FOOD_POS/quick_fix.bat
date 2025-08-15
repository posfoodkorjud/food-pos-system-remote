@echo off
chcp 65001 >nul
echo.
echo 🔧 Quick Fix Tool สำหรับปัญหา Database Schema
echo =====================================================
echo.

:menu
echo เลือกการดำเนินการ:
echo 1. ตรวจสอบความสอดคล้อง (Check Consistency)
echo 2. แก้ไขอัตโนมัติ (Auto Fix)
echo 3. ทดสอบ API (Test API)
echo 4. สำรองฐานข้อมูล (Backup Database)
echo 5. ออกจากโปรแกรม (Exit)
echo.
set /p choice="กรุณาเลือก (1-5): "

if "%choice%"=="1" goto check
if "%choice%"=="2" goto fix
if "%choice%"=="3" goto test
if "%choice%"=="4" goto backup
if "%choice%"=="5" goto exit
echo ❌ ตัวเลือกไม่ถูกต้อง
goto menu

:check
echo.
echo 🔍 กำลังตรวจสอบความสอดคล้อง...
python database_consistency_check.py
echo.
pause
goto menu

:fix
echo.
echo ⚠️  คำเตือน: การแก้ไขอัตโนมัติจะเปลี่ยนแปลงไฟล์โค้ด
set /p confirm="ต้องการดำเนินการต่อหรือไม่? (y/n): "
if /i "%confirm%"=="y" (
    echo 🔧 กำลังแก้ไขอัตโนมัติ...
    python fix_special_request.py
    echo ✅ เสร็จสิ้นการแก้ไข
) else (
    echo ❌ ยกเลิกการแก้ไข
)
echo.
pause
goto menu

:test
echo.
echo 🧪 กำลังทดสอบ API...
echo กำลังทดสอบ /api/orders...
curl -X GET http://localhost:5000/api/orders -w "\nStatus: %%{http_code}\n" -s
echo.
echo กำลังทดสอบ /api/tables...
curl -X GET http://localhost:5000/api/tables -w "\nStatus: %%{http_code}\n" -s
echo.
pause
goto menu

:backup
echo.
echo 💾 กำลังสำรองฐานข้อมูล...
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "datestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"
copy pos_database.db pos_database_backup_%datestamp%.db
echo ✅ สำรองฐานข้อมูลเรียบร้อย: pos_database_backup_%datestamp%.db
echo.
pause
goto menu

:exit
echo.
echo 👋 ขอบคุณที่ใช้ Quick Fix Tool
exit /b 0