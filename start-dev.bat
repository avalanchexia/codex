@echo off
chcp 65001 >nul
echo ===== Starting Codex Development Environment =====
echo.

REM Check necessary dependencies
echo Checking development environment...

REM Check Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found, please install Node.js first
    pause
    exit /b 1
)

REM Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found, please install Python first
    pause
    exit /b 1
)

REM Check LangGraph CLI
python -c "import langgraph_cli" >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] LangGraph CLI not found, please run: pip install langgraph-cli
    pause
    exit /b 1
)

echo [OK] Development environment check passed

REM Set environment variables
echo.
echo Setting environment variables...
set GEMINI_API_KEY=AIzaSyCB2cI-2SYqvtuLQJoc7FXhMK7I0nkpBDk
set LANGSMITH_API_KEY=
set LANGCHAIN_VERBOSE=false
set LANGCHAIN_TRACING_V2=false

echo [OK] Environment variables set

REM Create backend .env file if not exists
if not exist "backend\.env" (
    echo.
    echo Creating backend .env file...
    echo GEMINI_API_KEY=AIzaSyCB2cI-2SYqvtuLQJoc7FXhMK7I0nkpBDk > backend\.env
    echo LANGSMITH_API_KEY= >> backend\.env
    echo [OK] Created backend .env file
)

REM Ask whether to run API test
echo.
set /p run_test="Run API connection test? (y/N): "
if /i "%run_test%"=="y" (
    echo.
    echo Running API connection test...
    cd backend
    python test_api_connection.py
    if %errorlevel% neq 0 (
        echo [WARNING] API test failed, but continuing to start services...
        echo Please check network connection and API key configuration
    ) else (
        echo [OK] API test passed
    )
    cd ..
)

echo.
echo ===== Starting Development Servers =====

echo.
echo [1/2] Starting frontend development server...
start "Frontend Dev Server" cmd /k "cd frontend && npm run dev"

echo.
echo [2/2] Starting backend development server...
start "Backend Dev Server" cmd /k "cd backend && langgraph up --config=langgraph.json --host=0.0.0.0 --port=8123"

echo.
echo ===== Development Servers Started =====
echo.
echo Service URLs:
echo   Frontend App:     http://localhost:5173/app/
echo   Backend API:      http://localhost:8123
echo   LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://localhost:8123
echo.
echo Notes:
echo   - If backend is unresponsive, check GEMINI_API_KEY configuration
echo   - Check console logs for detailed error information
echo   - Use Ctrl+C to stop each service
echo.
echo Press any key to exit startup script...
pause 