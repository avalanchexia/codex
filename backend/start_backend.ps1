# PowerShell 脚本：启动后端服务
# 确保环境变量正确设置并启动 LangGraph 服务

Write-Host "=== 启动 Codex 后端服务 ===" -ForegroundColor Green

# 检查是否在正确的目录
if (-not (Test-Path "src/agent/graph.py")) {
    Write-Host "错误: 请在 backend 目录下运行此脚本" -ForegroundColor Red
    exit 1
}

# 检查 .env 文件是否存在
if (-not (Test-Path ".env")) {
    Write-Host "警告: .env 文件不存在，正在创建..." -ForegroundColor Yellow
    @"
GEMINI_API_KEY=AIzaSyCB2cI-2SYqvtuLQJoc7FXhMK7I0nkpBDk
LANGSMITH_API_KEY=lsv2_pt_placeholder_for_development
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "已创建 .env 文件" -ForegroundColor Green
}

# 加载环境变量
Write-Host "加载环境变量..." -ForegroundColor Blue
Get-Content ".env" | ForEach-Object {
    if ($_ -match "^([^=]+)=(.*)$") {
        $name = $matches[1]
        $value = $matches[2]
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
        Write-Host "设置环境变量: $name" -ForegroundColor Gray
    }
}

# 验证关键环境变量
$geminiKey = [Environment]::GetEnvironmentVariable("GEMINI_API_KEY", "Process")
if (-not $geminiKey) {
    Write-Host "错误: GEMINI_API_KEY 未设置" -ForegroundColor Red
    exit 1
}

if (-not $geminiKey.StartsWith("AIza")) {
    Write-Host "警告: GEMINI_API_KEY 格式可能不正确" -ForegroundColor Yellow
}

Write-Host "✅ GEMINI_API_KEY 已设置: $($geminiKey.Substring(0, 10))..." -ForegroundColor Green

# 运行 API 连接测试（可选）
$runTest = Read-Host "是否运行 API 连接测试？(y/N)"
if ($runTest -eq "y" -or $runTest -eq "Y") {
    Write-Host "运行 API 连接测试..." -ForegroundColor Blue
    python test_api_connection.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "API 测试失败，但继续启动服务..." -ForegroundColor Yellow
    }
}

# 启动 LangGraph 服务
Write-Host "启动 LangGraph 服务..." -ForegroundColor Blue
Write-Host "服务将在 http://localhost:8123 启动" -ForegroundColor Green
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Gray

# 设置详细日志级别
$env:LANGCHAIN_VERBOSE = "true"
$env:LANGCHAIN_TRACING_V2 = "true"

# 启动服务
langgraph up --config=langgraph.json --host=0.0.0.0 --port=8123 