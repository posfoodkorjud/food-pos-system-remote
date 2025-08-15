#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Food POS System - Executable Builder
สคริปต์สำหรับสร้างไฟล์ .exe จากระบบ POS

This script creates a standalone executable file for the Food POS system
using PyInstaller, making it easy to distribute and run on any Windows machine.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """
    ตรวจสอบว่า PyInstaller ติดตั้งแล้วหรือไม่
    """
    try:
        import PyInstaller
        print("✅ พบ PyInstaller แล้ว")
        return True
    except ImportError:
        print("⚠️  ไม่พบ PyInstaller กำลังติดตั้ง...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ ติดตั้ง PyInstaller เสร็จแล้ว")
            return True
        except subprocess.CalledProcessError:
            print("❌ ไม่สามารถติดตั้ง PyInstaller ได้")
            return False

def create_spec_file():
    """
    สร้างไฟล์ .spec สำหรับ PyInstaller
    """
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('frontend', 'frontend'),
        ('backend', 'backend'),
        ('.env', '.'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'qrcode',
        'PIL',
        'sqlite3',
        'threading',
        'webbrowser',
        'pathlib',
        'base64',
        'io',
        'datetime',
        'json',
        'os',
        'sys',
        'time',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FoodPOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('FoodPOS.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ สร้างไฟล์ FoodPOS.spec แล้ว")

def create_launcher_script():
    """
    สร้างสคริปต์ launcher สำหรับ executable
    """
    launcher_content = '''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Food POS System - Executable Launcher
ตัวเริ่มต้นระบบ POS สำหรับไฟล์ executable
"""

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Add the executable directory to Python path
if getattr(sys, 'frozen', False):
    # Running as executable
    application_path = os.path.dirname(sys.executable)
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, application_path)
os.chdir(application_path)

try:
    from backend.database import DatabaseManager
    from backend.app import app
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please make sure all files are in the correct location.")
    input("Press Enter to exit...")
    sys.exit(1)

def initialize_database():
    """
    Initialize the database with default data
    """
    print("กำลังเริ่มต้นฐานข้อมูล...")
    try:
        db = DatabaseManager()
        db.initialize_database()
        print("✅ เริ่มต้นฐานข้อมูลเสร็จแล้ว!")
        return True
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเริ่มต้นฐานข้อมูล: {e}")
        return False

def open_admin_panel(host='localhost', port=5000, delay=3):
    """
    Open the admin panel in the default web browser
    """
    def delayed_open():
        time.sleep(delay)
        admin_url = f"http://{host}:{port}/admin.html"
        print(f"🌐 เปิด Admin Panel: {admin_url}")
        try:
            webbrowser.open(admin_url)
        except Exception as e:
            print(f"ไม่สามารถเปิดเบราว์เซอร์อัตโนมัติได้: {e}")
            print(f"กรุณาเปิดเบราว์เซอร์และไปที่: {admin_url}")
    
    thread = threading.Thread(target=delayed_open, daemon=True)
    thread.start()

def print_banner():
    """
    Print the application banner
    """
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🍽️  FOOD POS SYSTEM  🍽️                    ║
║                  ระบบ POS สำหรับร้านอาหาร                     ║
║                     (Executable Version)                    ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """
    Main function for executable
    """
    print_banner()
    
    # Initialize database
    print("🗄️  กำลังตั้งค่าฐานข้อมูล...")
    if not initialize_database():
        print("❌ ไม่สามารถเริ่มต้นฐานข้อมูลได้!")
        input("กด Enter เพื่อออก...")
        sys.exit(1)
    
    # Configuration
    HOST = 'localhost'
    PORT = 5000
    
    print("\n" + "="*60)
    print("🚀 FOOD POS SYSTEM เริ่มต้นเสร็จแล้ว!")
    print("="*60)
    print(f"📊 Admin Panel:     http://{HOST}:{PORT}/admin.html")
    print(f"📱 Customer App:    http://{HOST}:{PORT}/")
    print(f"🔧 API Endpoint:    http://{HOST}:{PORT}/api/")
    print("="*60)
    print("\n📋 คำแนะนำการใช้งาน:")
    print("1. เปิด Admin Panel เพื่อจัดการโต๊ะและเมนู")
    print("2. สร้าง QR Code สำหรับโต๊ะ")
    print("3. ตั้งค่า PromptPay และ Google Sheets")
    print("4. ลูกค้าสแกน QR Code เพื่อสั่งอาหาร")
    print("\n⚠️  กด Ctrl+C เพื่อหยุดเซิร์ฟเวอร์")
    print("="*60)
    
    # Open admin panel automatically
    open_admin_panel(HOST, PORT)
    
    # Start web server
    print("\n🌐 กำลังเริ่มต้นเว็บเซิร์ฟเวอร์...")
    try:
        app.run(host=HOST, port=PORT, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n🛑 เซิร์ฟเวอร์หยุดทำงานแล้ว")
        print("ขอบคุณที่ใช้ระบบ Food POS!")
        input("กด Enter เพื่อออก...")
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาดในเซิร์ฟเวอร์: {e}")
        input("กด Enter เพื่อออก...")
        sys.exit(1)

if __name__ == '__main__':
    main()
'''
    
    with open('launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("✅ สร้างไฟล์ launcher.py แล้ว")

def build_executable():
    """
    สร้างไฟล์ executable
    """
    print("🔨 กำลังสร้างไฟล์ executable...")
    print("   (อาจใช้เวลาสักครู่)")
    
    try:
        # Run PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "FoodPOS.spec"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ สร้างไฟล์ executable เสร็จแล้ว!")
            
            # Check if executable exists
            exe_path = Path("dist/FoodPOS.exe")
            if exe_path.exists():
                print(f"📁 ไฟล์ executable อยู่ที่: {exe_path.absolute()}")
                print(f"📏 ขนาดไฟล์: {exe_path.stat().st_size / (1024*1024):.1f} MB")
                return True
            else:
                print("❌ ไม่พบไฟล์ executable ที่สร้างแล้ว")
                return False
        else:
            print("❌ เกิดข้อผิดพลาดในการสร้าง executable")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def cleanup():
    """
    ทำความสะอาดไฟล์ชั่วคราว
    """
    print("🧹 กำลังทำความสะอาดไฟล์ชั่วคราว...")
    
    # Remove build directory
    if os.path.exists("build"):
        shutil.rmtree("build")
        print("   ลบโฟลเดอร์ build แล้ว")
    
    # Remove spec file
    if os.path.exists("FoodPOS.spec"):
        os.remove("FoodPOS.spec")
        print("   ลบไฟล์ FoodPOS.spec แล้ว")
    
    # Remove launcher file
    if os.path.exists("launcher.py"):
        os.remove("launcher.py")
        print("   ลบไฟล์ launcher.py แล้ว")
    
    print("✅ ทำความสะอาดเสร็จแล้ว")

def create_readme_for_exe():
    """
    สร้างไฟล์ README สำหรับ executable
    """
    readme_content = '''
# 🍽️ Food POS System - Executable Version

## 🚀 วิธีการใช้งาน

1. **เริ่มต้นระบบ**: ดับเบิลคลิก `FoodPOS.exe`
2. **รอให้ระบบเริ่มต้น**: ระบบจะเปิดหน้าต่าง Command Prompt และเริ่มต้นเซิร์ฟเวอร์
3. **เข้าถึงระบบ**: เบราว์เซอร์จะเปิดหน้า Admin Panel อัตโนมัติ

## 🌐 URL สำหรับเข้าถึง

- **Admin Panel**: http://localhost:5000/admin.html
- **Customer App**: http://localhost:5000/
- **API**: http://localhost:5000/api/

## ⚠️ ข้อควรระวัง

- **อย่าปิดหน้าต่าง Command Prompt** ขณะที่ระบบทำงาน
- **กด Ctrl+C** ในหน้าต่าง Command Prompt เพื่อหยุดระบบ
- **ตรวจสอบ Firewall** หากลูกค้าไม่สามารถเข้าถึงได้

## 🔧 การแก้ไขปัญหา

### ระบบไม่เริ่มต้น
- ตรวจสอบว่าไม่มีโปรแกรมอื่นใช้ port 5000
- รันในฐานะ Administrator
- ตรวจสอบ Windows Defender/Antivirus

### ลูกค้าเข้าถึงไม่ได้
- ตรวจสอบ Windows Firewall
- ใช้ IP address แทน localhost
- ตรวจสอบการเชื่อมต่อเครือข่าย

## 📞 การสนับสนุน

หากพบปัญหาการใช้งาน กรุณาตรวจสอบไฟล์ README.md ฉบับเต็มสำหรับข้อมูลเพิ่มเติม
'''
    
    with open("dist/README_EXE.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ สร้างไฟล์ README_EXE.txt แล้ว")

def main():
    """
    ฟังก์ชันหลักสำหรับสร้าง executable
    """
    print("\n" + "="*60)
    print("🔨 FOOD POS SYSTEM - EXECUTABLE BUILDER")
    print("   สร้างไฟล์ .exe สำหรับระบบ POS")
    print("="*60)
    
    # Check current directory
    if not os.path.exists("main.py"):
        print("❌ ไม่พบไฟล์ main.py")
        print("   กรุณารันสคริปต์นี้ในโฟลเดอร์ FOOD_POS")
        input("กด Enter เพื่อออก...")
        return
    
    # Check PyInstaller
    if not check_pyinstaller():
        input("กด Enter เพื่อออก...")
        return
    
    # Create necessary files
    create_spec_file()
    create_launcher_script()
    
    # Build executable
    if build_executable():
        # Create README for executable
        create_readme_for_exe()
        
        print("\n" + "="*60)
        print("🎉 สร้างไฟล์ executable เสร็จแล้ว!")
        print("="*60)
        print("📁 ไฟล์ที่สร้าง:")
        print("   - dist/FoodPOS.exe (ไฟล์หลัก)")
        print("   - dist/README_EXE.txt (คำแนะนำการใช้งาน)")
        print("\n📋 วิธีการใช้งาน:")
        print("   1. คัดลอกโฟลเดอร์ 'dist' ไปยังเครื่องที่ต้องการใช้งาน")
        print("   2. ดับเบิลคลิก FoodPOS.exe เพื่อเริ่มต้นระบบ")
        print("   3. ระบบจะเปิดเบราว์เซอร์ไปยัง Admin Panel อัตโนมัติ")
        print("\n⚠️  หมายเหตุ:")
        print("   - ไฟล์ .exe ใช้งานได้บน Windows เท่านั้น")
        print("   - ขนาดไฟล์อาจใหญ่เนื่องจากรวม Python runtime")
        print("   - การรันครั้งแรกอาจใช้เวลาสักครู่")
        
        # Ask for cleanup
        print("\n🧹 ต้องการลบไฟล์ชั่วคราวหรือไม่? (y/n): ", end="")
        choice = input().lower().strip()
        if choice in ['y', 'yes', 'ใช่']:
            cleanup()
        
        print("\n✅ เสร็จสิ้น!")
    else:
        print("\n❌ ไม่สามารถสร้างไฟล์ executable ได้")
        print("กรุณาตรวจสอบข้อผิดพลาดด้านบนและลองใหม่")
    
    input("\nกด Enter เพื่อออก...")

if __name__ == "__main__":
    main()