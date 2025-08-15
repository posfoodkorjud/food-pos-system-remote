@echo off
chcp 65001 >nul
echo ========================================
echo Food POS System - Executable Builder
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)
echo Python found!
echo.

echo Checking main.py file...
if not exist "main.py" (
    echo ERROR: main.py not found!
    echo Please make sure you are in the correct directory
    pause
    exit /b 1
)
echo main.py found!
echo.

echo ========================================
echo Building executable file...
echo ========================================
echo This process may take several minutes...
echo - Installing PyInstaller automatically if needed
echo - Creating single executable file
echo - Including all dependencies
echo - Adding icon (if available)
echo.

echo Running build script...
python build_exe.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Common solutions:
    echo 1. Make sure all Python dependencies are installed
    echo 2. Check if antivirus is blocking the process
    echo 3. Run as administrator if needed
    echo 4. Check build_exe.py for detailed error messages
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo The executable file has been created in the 'dist' folder
echo You can now run the Food POS system by double-clicking the .exe file
echo.
echo Location: dist\Food_POS.exe
echo.
echo Press any key to open the dist folder...
pause >nul
explorer dist