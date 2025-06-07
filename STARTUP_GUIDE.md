# 🚀 项目启动指南

## 📋 概述

这是一个基于 LangGraph 和 React 的全栈研究助手应用。本指南将帮助您快速启动开发环境。

## 🛠️ 前置要求

- **Node.js** (v16 或更高版本)
- **Python** (v3.11 或更高版本)
- **Gemini API 密钥** (可选，用于完整功能)

## 🎯 启动方式

### 方式 1: 增强版 PowerShell 脚本 (推荐)

```powershell
# 基本启动 (使用占位符 API 密钥)
.\start-dev.ps1

# 使用真实 API 密钥启动
.\start-dev.ps1 -GeminiApiKey "您的_Gemini_API_密钥"

# 跳过依赖安装 (如果已安装)
.\start-dev.ps1 -SkipInstall

# 详细输出模式
.\start-dev.ps1 -Verbose
```

### 方式 2: 批处理文件

```cmd
start-dev.bat
```

### 方式 3: 手动启动

**前端 (PowerShell 窗口 1):**

```powershell
cd frontend
npm run dev
```

**后端 (PowerShell 窗口 2):**

```powershell
cd backend
pip install -e .  # 首次运行需要
$env:GEMINI_API_KEY="您的API密钥"
python -m langgraph_cli dev --allow-blocking --no-browser
```

## 🌐 访问地址

启动成功后，您可以访问：

- **前端应用**: http://localhost:5173/app/
- **后端 API**: http://127.0.0.1:2024
- **API 文档**: http://127.0.0.1:2024/docs
- **LangGraph Studio**: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

## 🔧 新增功能

增强版脚本 `start-dev.ps1` 包含以下新功能：

### ✅ 环境检查

- 自动检查 Node.js 和 Python 安装
- 验证项目结构完整性
- 显示版本信息

### 📦 依赖管理

- 自动安装后端依赖 (`pip install -e .`)
- 可选跳过安装 (`-SkipInstall`)

### 🔍 启动监控

- 实时检查端口状态
- 启动超时检测 (前端 30s, 后端 45s)
- 彩色状态提示

### 📊 状态监控

- 每 5 秒检查服务器状态
- 实时显示前后端运行状态
- 优雅的停止机制

### 🔑 API 密钥管理

- 支持命令行传入 API 密钥
- 占位符模式警告提示
- 获取 API 密钥的指导链接

## ⚠️ 常见问题

### 1. LangGraph 启动失败

**症状**: 后端显示启动但端口 2024 无响应

**解决方案**:

1. 确保在 `backend` 目录运行
2. 先运行 `pip install -e .` 安装项目
3. 检查 Python 版本 (需要 3.11+)
4. 使用 `--allow-blocking` 参数

### 2. 端口被占用

**症状**: 端口 5173 或 2024 被占用

**解决方案**:

```powershell
# 查找占用端口的进程
netstat -ano | findstr ":5173"
netstat -ano | findstr ":2024"

# 杀死进程 (替换 PID)
taskkill /f /pid [PID]
```

### 3. 权限问题

**症状**: PowerShell 脚本执行被阻止

**解决方案**:

```powershell
# 临时允许执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 或者直接运行
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1
```

### 4. API 密钥问题

**症状**: 后端功能受限或报错

**解决方案**:

1. 获取真实的 [Gemini API 密钥](https://aistudio.google.com/app/apikey)
2. 创建 `backend/.env` 文件：
   ```
   GEMINI_API_KEY=您的真实API密钥
   ```
3. 或使用参数传递：
   ```powershell
   .\start-dev.ps1 -GeminiApiKey "您的API密钥"
   ```

## 🛑 停止服务

- **增强版脚本**: 按 `Ctrl+C` 会自动清理所有后台任务
- **手动启动**: 在各自窗口按 `Ctrl+C`
- **强制停止**: 使用 `taskkill` 命令

## 📝 开发建议

1. **首次运行**: 使用 `.\start-dev.ps1 -Verbose` 查看详细信息
2. **日常开发**: 使用 `.\start-dev.ps1 -SkipInstall` 跳过依赖检查
3. **调试问题**: 查看各自服务器窗口的详细日志
4. **生产部署**: 参考 README.md 中的 Docker 部署方式
