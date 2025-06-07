#!/usr/bin/env pwsh

# 增强版开发服务器启动脚本
param(
    [string]$GeminiApiKey = "placeholder",
    [switch]$SkipInstall,
    [switch]$Verbose
)

function Write-Status {
    param([string]$Message, [string]$Color = "White")
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] $Message" -ForegroundColor $Color
}

function Test-Port {
    param([int]$Port)
    try {
        $connection = Test-NetConnection -ComputerName "localhost" -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
        return $connection
    }
    catch {
        return $false
    }
}

# 环境检查
Write-Status "Checking development environment..." "Yellow"

# Check Node.js
if (-not (Get-Command "node" -ErrorAction SilentlyContinue)) {
    Write-Status "ERROR: Node.js not installed or not in PATH" "Red"
    exit 1
}
Write-Status "OK: Node.js installed: $(node --version)" "Green"

# Check Python
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Status "ERROR: Python not installed or not in PATH" "Red"
    exit 1
}
Write-Status "OK: Python installed: $(python --version)" "Green"

# Check project structure
if (-not (Test-Path "frontend/package.json")) {
    Write-Status "ERROR: Frontend project missing or incorrect structure" "Red"
    exit 1
}

if (-not (Test-Path "backend/langgraph.json")) {
    Write-Status "ERROR: Backend config missing or incorrect structure" "Red"
    exit 1
}

Write-Status "OK: Project structure validated" "Green"

# Install dependencies
if (-not $SkipInstall) {
    Write-Status "Installing backend dependencies..." "Yellow"
    Push-Location "backend"
    try {
        $installOutput = pip install -e . 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "OK: Backend dependencies installed" "Green"
        } else {
            Write-Status "WARNING: Backend install may have issues, continuing..." "Yellow"
            if ($Verbose) { Write-Host $installOutput }
        }
    }
    finally {
        Pop-Location
    }
}

# Start frontend server
Write-Status "Starting frontend development server..." "Yellow"
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "frontend"
    npm run dev
}

# Wait for frontend startup
Write-Status "Waiting for frontend server to start..." "Yellow"
$frontendStartTime = Get-Date
$frontendTimeout = 30 # 30秒超时

do {
    Start-Sleep -Seconds 2
    $frontendRunning = Test-Port -Port 5173
    $elapsed = (Get-Date) - $frontendStartTime
} while (-not $frontendRunning -and $elapsed.TotalSeconds -lt $frontendTimeout)

if ($frontendRunning) {
    Write-Status "OK: Frontend server started (http://localhost:5173/app/)" "Green"
} else {
    Write-Status "WARNING: Frontend startup timeout, continuing with backend..." "Yellow"
}

# Start backend server
Write-Status "Starting backend development server..." "Yellow"
$backendJob = Start-Job -ScriptBlock {
    param($ApiKey)
    Set-Location "backend"
    $env:GEMINI_API_KEY = $ApiKey
    python -m langgraph_cli dev --allow-blocking --no-browser
} -ArgumentList $GeminiApiKey

# Wait for backend startup
Write-Status "Waiting for backend server to start..." "Yellow"
$backendStartTime = Get-Date
$backendTimeout = 45 # 45 second timeout

do {
    Start-Sleep -Seconds 3
    $backendRunning = Test-Port -Port 2024
    $elapsed = (Get-Date) - $backendStartTime
} while (-not $backendRunning -and $elapsed.TotalSeconds -lt $backendTimeout)

if ($backendRunning) {
    Write-Status "OK: Backend server started (http://127.0.0.1:2024)" "Green"
} else {
    Write-Status "WARNING: Backend may have failed to start or still initializing" "Yellow"
}

# Display status and access information
Write-Host ""
Write-Status "Development servers startup complete!" "Green"
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "  Frontend App: http://localhost:5173/app/" -ForegroundColor White
Write-Host "  Backend API: http://127.0.0.1:2024" -ForegroundColor White
Write-Host "  API Docs: http://127.0.0.1:2024/docs" -ForegroundColor White
Write-Host "  LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024" -ForegroundColor White
Write-Host ""

if ($GeminiApiKey -eq "placeholder") {
    Write-Host "WARNING: Using placeholder API key, some features may be limited" -ForegroundColor Yellow
    Write-Host "   For full functionality:" -ForegroundColor Yellow
    Write-Host "   1. Get Gemini API key: https://aistudio.google.com/app/apikey" -ForegroundColor Yellow
    Write-Host "   2. Re-run: .\start-dev.ps1 -GeminiApiKey 'your-api-key'" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Red
Write-Host ""

# 监控服务器状态
try {
    while ($true) {
        $frontendRunning = Test-Port -Port 5173
        $backendRunning = Test-Port -Port 2024
        
        $status = @()
        if ($frontendRunning) { $status += "Frontend OK" } else { $status += "Frontend DOWN" }
        if ($backendRunning) { $status += "Backend OK" } else { $status += "Backend DOWN" }
        
        Write-Host "`r[$((Get-Date).ToString('HH:mm:ss'))] Status: $($status -join ' | ')" -NoNewline
        
        Start-Sleep -Seconds 5
    }
}
catch {
    Write-Host ""
    Write-Status "Received stop signal..." "Yellow"
}
finally {
    # Cleanup tasks
    Write-Status "Cleaning up background tasks..." "Yellow"
    Stop-Job $frontendJob, $backendJob -ErrorAction SilentlyContinue
    Remove-Job $frontendJob, $backendJob -ErrorAction SilentlyContinue
    Write-Status "All servers stopped" "Red"
} 