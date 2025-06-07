@echo off
echo ========================================
echo 调试启动脚本
echo ========================================

echo.
echo 1. 检查项目目录结构...
if exist "frontend\package.json" (
    echo ✓ 前端目录存在
) else (
    echo ✗ 前端目录不存在
    pause
    exit /b 1
)

if exist "backend\langgraph.json" (
    echo ✓ 后端配置文件存在
) else (
    echo ✗ 后端配置文件不存在
    pause
    exit /b 1
)

echo.
echo 2. 检查依赖...
echo 检查 Node.js...
where node >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Node.js 已安装
) else (
    echo ✗ Node.js 未安装
    pause
    exit /b 1
)

echo 检查 Python...
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python 已安装
) else (
    echo ✗ Python 未安装
    pause
    exit /b 1
)

echo.
echo 3. 启动前端开发服务器...
start "Frontend - 前端服务器" cmd /k "cd /d %~dp0frontend && echo 启动前端服务器... && npm run dev"

echo.
echo 4. 等待前端启动...
timeout /t 5 /nobreak >nul

echo.
echo 5. 启动后端开发服务器...
start "Backend - 后端服务器" cmd /k "cd /d %~dp0backend && echo 启动后端服务器... && set GEMINI_API_KEY=AIzaSyCB2cI-2SYqvtuLQJoc7FXhMK7I0nkpBDk && python -m langgraph_cli dev --allow-blocking"

echo.
echo ========================================
echo 服务启动完成！
echo ========================================
echo 前端: http://localhost:5173/app/
echo 后端: http://127.0.0.1:2024
echo ========================================
echo.
echo 注意：
echo 1. 如果看到错误，请检查对应的服务器窗口
echo 2. 已设置真实的 GEMINI_API_KEY，功能完整可用
echo 3. 关闭时请关闭所有打开的服务器窗口
echo.
pause 