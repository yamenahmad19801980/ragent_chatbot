# LangGraph Studio startup script for PowerShell
# This script starts LangGraph Studio for Ragent Chatbot development

Write-Host "🤖 Ragent Chatbot - LangGraph Studio Launcher" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python version: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and add it to your PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Change to project root directory
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found" -ForegroundColor Red
    Write-Host "Please create a .env file with required variables:" -ForegroundColor Yellow
    Write-Host "   QWEN_API_KEY=your_api_key" -ForegroundColor White
    Write-Host "   TAVILY_API_KEY=your_api_key" -ForegroundColor White
    Write-Host "   EMAIL=your_email" -ForegroundColor White
    Write-Host "   PASSWORD=your_password" -ForegroundColor White
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies if needed
Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import langgraph_studio" 2>$null
    Write-Host "✅ Dependencies are installed" -ForegroundColor Green
}
catch {
    Write-Host "🔧 Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Test graph compilation
Write-Host "🧪 Testing graph compilation..." -ForegroundColor Yellow
try {
    python -c "from agent import get_compiled_graph; print('Graph compiled successfully')" 2>$null
    Write-Host "✅ Graph compiled successfully" -ForegroundColor Green
}
catch {
    Write-Host "❌ Graph compilation failed" -ForegroundColor Red
    Write-Host "Please check your code and dependencies" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Start LangGraph Studio
Write-Host "🚀 Starting LangGraph Studio..." -ForegroundColor Green
Write-Host "🌐 Studio will be available at: http://localhost:8123" -ForegroundColor Cyan
Write-Host "📖 See studio/README.md for usage instructions" -ForegroundColor Cyan
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🎯 LangGraph Studio is starting..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

try {
    langgraph-studio --config studio/langgraph.json --port 8123
}
catch {
    Write-Host "❌ Failed to start LangGraph Studio" -ForegroundColor Red
    Write-Host "Please check the error messages above" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "👋 LangGraph Studio stopped" -ForegroundColor Green
Read-Host "Press Enter to exit"
