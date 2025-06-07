@echo off
chcp 936 >nul
echo ===== 启动 Codex 开发环境 =====
echo.

REM 检查必要的依赖
echo 检查开发环境...

REM 检查 Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

REM 检查 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

REM 检查 LangGraph CLI
python -c "import langgraph_cli" >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 LangGraph CLI，请运行: pip install langgraph-cli
    pause
    exit /b 1
)

echo [成功] 开发环境检查通过

REM 设置环境变量
echo.
echo 设置环境变量...
set GEMINI_API_KEY=AIzaSyCB2cI-2SYqvtuLQJoc7FXhMK7I0nkpBDk
set LANGSMITH_API_KEY=
set LANGCHAIN_VERBOSE=false
set LANGCHAIN_TRACING_V2=false

echo [成功] 环境变量已设置

REM 创建后端 .env 文件（如果不存在）
if not exist "backend\.env" (
    echo.
    echo 创建后端 .env 文件...
    echo GEMINI_API_KEY=AIzaSyCB2cI-2SYqvtuLQJoc7FXhMK7I0nkpBDk > backend\.env
    echo LANGCHAIN_TRACING_V2=false >> backend\.env
    echo [成功] 已创建 backend\.env 文件
)

REM 询问是否运行 API 测试
echo.
set /p run_test="是否运行 API 连接测试？(y/N): "
if /i "%run_test%"=="y" (
    echo.
    echo 运行 API 连接测试...
    cd backend
    python test_api_connection.py
    if %errorlevel% neq 0 (
        echo [警告] API 测试失败，但继续启动服务...
        echo 请检查网络连接和 API 密钥配置
    ) else (
        echo [成功] API 测试通过
    )
    cd ..
)

echo.
echo ===== 启动开发服务器 =====

echo.
echo [1/2] 启动前端开发服务器...
start "Frontend Dev Server" cmd /k "chcp 936 && cd frontend && npm run dev"

echo.
echo [2/2] 启动后端开发服务器...
start "Backend Dev Server" cmd /k "chcp 936 && cd backend && set LANGCHAIN_TRACING_V2=false && langgraph up --config=langgraph.json --host=0.0.0.0 --port=8123"

echo.
echo ===== 开发服务器启动完成 =====
echo.
echo 服务地址:
echo   前端应用:     http://localhost:5173/app/
echo   后端 API:     http://localhost:8123
echo   LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://localhost:8123
echo.
echo 注意事项:
echo   - 如果后端无响应，请检查 GEMINI_API_KEY 配置
echo   - 查看控制台日志以获取详细错误信息
echo   - 使用 Ctrl+C 停止各个服务
echo   - 已禁用 LangSmith 追踪以避免 403 错误
echo.
echo 按任意键退出启动脚本...
pause 