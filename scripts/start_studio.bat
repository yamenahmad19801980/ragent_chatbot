@echo off
REM LangGraph Studio startup script for Windows
REM This script starts LangGraph Studio for Ragent Chatbot development

echo 🤖 Ragent Chatbot - LangGraph Studio Launcher
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

REM Change to project root directory
cd /d "%~dp0.."

REM Check if .env file exists
if not exist ".env" (
    echo ❌ .env file not found
    echo Please create a .env file with required variables:
    echo    QWEN_API_KEY=your_api_key
    echo    TAVILY_API_KEY=your_api_key
    echo    EMAIL=your_email
    echo    PASSWORD=your_password
    pause
    exit /b 1
)

REM Install dependencies if needed
echo 📦 Checking dependencies...
python -c "import langgraph_studio" >nul 2>&1
if errorlevel 1 (
    echo 🔧 Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Test graph compilation
echo 🧪 Testing graph compilation...
python -c "from agent import get_compiled_graph; print('Graph compiled successfully')" >nul 2>&1
if errorlevel 1 (
    echo ❌ Graph compilation failed
    echo Please check your code and dependencies
    pause
    exit /b 1
)

REM Start LangGraph Studio
echo 🚀 Starting LangGraph Studio...
echo 🌐 Studio will be available at: http://localhost:8123
echo 📖 See studio/README.md for usage instructions
echo.
echo ================================================
echo 🎯 LangGraph Studio is starting...
echo ================================================
echo.

langgraph-studio --config studio/langgraph.json --port 8123

if errorlevel 1 (
    echo ❌ Failed to start LangGraph Studio
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo 👋 LangGraph Studio stopped
pause
