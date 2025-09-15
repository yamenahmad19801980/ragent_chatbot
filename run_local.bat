@echo off
echo 🏠 Smart Home Assistant - Local Runner
echo =====================================

REM Check if Python exists
if not exist "C:\Program Files\Odoo 18.0e.20241014\python\python.exe" (
    echo ❌ Python not found at expected location
    echo Please update the path in this batch file
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found
    echo Please create a .env file with your API keys
    echo See LOCAL_TESTING.md for details
    pause
    exit /b 1
)

echo 🔍 Running tests...
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" test_local.py

echo.
echo 🚀 Starting Smart Home Assistant...
echo Open your browser and go to: http://localhost:7860
echo Press Ctrl+C to stop the application
echo.

"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" app.py

pause
