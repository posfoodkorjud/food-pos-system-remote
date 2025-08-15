#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Food POS System - Main Entry Point
ระบบ POS สำหรับร้านอาหาร

This is the main entry point for the Food POS system.
It initializes the database and starts the Flask web server.
"""

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from backend.database import DatabaseManager
    from backend.app import app
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please make sure all dependencies are installed.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

def initialize_database():
    """
    Initialize the database with default data
    """
    print("Initializing database...")
    try:
        db = DatabaseManager()
        # เรียกใช้เฉพาะ init_database() เพื่อสร้างโครงสร้างฐานข้อมูล
        # แต่ไม่เรียกใช้ initialize_database() ที่จะสร้างข้อมูลเริ่มต้น
        db.init_database()
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def start_web_server(host='localhost', port=5000, debug=True):
    """
    Start the Flask web server
    """
    print(f"Starting web server on http://{host}:{port}")
    try:
        app.run(host=host, port=port, debug=debug, threaded=True)
    except Exception as e:
        print(f"Error starting web server: {e}")
        return False

def open_admin_panel(host='localhost', port=5000, delay=3):
    """
    Open the admin panel in the default web browser
    """
    def delayed_open():
        time.sleep(delay)
        admin_url = f"http://{host}:{port}/admin"
        print(f"Opening admin panel: {admin_url}")
        try:
            webbrowser.open(admin_url)
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print(f"Please open your browser and go to: {admin_url}")
    
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
║                                                              ║
║  📱 Customer Web App  |  🖥️  Admin Panel  |  📊 Analytics    ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_startup_info(host='localhost', port=5000):
    """
    Print startup information
    """
    print("\n" + "="*60)
    print("🚀 FOOD POS SYSTEM STARTED SUCCESSFULLY!")
    print("="*60)
    print(f"📊 Admin Panel:     http://{host}:{port}/admin")
    print(f"📱 Customer App:    http://{host}:{port}/")
    print(f"🔧 API Endpoint:    http://{host}:{port}/api/")
    print("="*60)
    print("\n📋 Quick Start Guide:")
    print("1. Open Admin Panel to manage tables and menu")
    print("2. Generate QR codes for tables")
    print("3. Configure PromptPay and Google Sheets")
    print("4. Customers scan QR codes to order food")
    print("\n⚠️  Press Ctrl+C to stop the server")
    print("="*60)

def check_dependencies():
    """
    Check if all required dependencies are available
    """
    required_modules = [
        'flask',
        'qrcode',
        'PIL',  # Pillow
        'sqlite3'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Missing required dependencies:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\n📦 Please install missing dependencies:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def main():
    """
    Main function
    """
    # Print banner
    print_banner()
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies are available!")
    
    # Initialize database
    print("\n🗄️  Setting up database...")
    if not initialize_database():
        print("❌ Failed to initialize database!")
        sys.exit(1)
    print("✅ Database setup complete!")
    
    # Configuration
    HOST = os.getenv('FOOD_POS_HOST', 'localhost')
    PORT = int(os.getenv('FOOD_POS_PORT', 5000))
    DEBUG = True  # Force debug mode to be enabled
    AUTO_OPEN = os.getenv('FOOD_POS_AUTO_OPEN', 'True').lower() == 'true'
    
    # Print startup info
    print_startup_info(HOST, PORT)
    
    # Open admin panel automatically
    if AUTO_OPEN:
        open_admin_panel(HOST, PORT)
    
    # Start web server
    print("\n🌐 Starting web server...")
    try:
        start_web_server(HOST, PORT, DEBUG)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("Thank you for using Food POS System!")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()