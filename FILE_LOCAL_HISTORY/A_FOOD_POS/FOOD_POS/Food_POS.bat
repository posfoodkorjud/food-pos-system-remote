@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo      Food POS System Launcher
echo ========================================
echo.
echo Starting Food POS System...
echo.

REM Try different Python commands
set PYTHON_CMD=
for %%i in (python py python3 python.exe) do (
    %%i --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=%%i
        goto :found_python
    )
)

echo ERROR: Python not found!
echo.
echo Please install Python from one of these sources:
echo 1. Microsoft Store (search for "Python")
echo 2. Official Python website: https://python.org
echo 3. Anaconda: https://anaconda.com
echo.
echo After installation, restart your computer and try again.
echo.
pause
exit /b 1

:found_python
echo Found Python: %PYTHON_CMD%
echo.

REM Install required packages if needed
echo Installing required packages...
%PYTHON_CMD% -m pip install flask flask-cors >nul 2>&1

REM Start the Flask server
echo Starting Food POS Server...
echo.
echo The system will open in your default web browser.
echo To stop the server, close this window or press Ctrl+C
echo.
echo Server URL: http://localhost:5000
echo Admin Panel: http://localhost:5000/admin
echo.

REM Wait a moment then open browser
start "" timeout /t 3 /nobreak >nul 2>&1
start "" http://localhost:5000/admin

REM Start the Flask application
%PYTHON_CMD% main.py

echo.
echo Food POS System has stopped.
pause