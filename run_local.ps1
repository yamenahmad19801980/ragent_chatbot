# Smart Home Assistant - Local Runner (PowerShell)
Write-Host "🏠 Smart Home Assistant - Local Runner" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if Python exists
$pythonPath = "C:\Program Files\Odoo 18.0e.20241014\python\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Host "❌ Python not found at expected location" -ForegroundColor Red
    Write-Host "Please update the path in this script" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "Please create a .env file with your API keys" -ForegroundColor Yellow
    Write-Host "See LOCAL_TESTING.md for details" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🔍 Running tests..." -ForegroundColor Green
& $pythonPath test_local.py

Write-Host ""
Write-Host "🚀 Starting Smart Home Assistant..." -ForegroundColor Green
Write-Host "Open your browser and go to: http://localhost:7860" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

& $pythonPath app.py

Read-Host "Press Enter to exit"
