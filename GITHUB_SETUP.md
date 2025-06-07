# 📚 GitHub 仓库设置指南

## 🎯 将项目保存到您的GitHub仓库

### 方法1：Fork原仓库（推荐）

这种方法保持与原项目的关联，便于后续获取更新。

#### 步骤1：在GitHub上Fork

1. 访问 [原始仓库](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart)
2. 点击右上角的 **"Fork"** 按钮
3. 选择您的GitHub账户创建Fork

#### 步骤2：更改本地远程仓库

```powershell
# 将远程仓库更改为您的Fork（替换YOUR_USERNAME为您的GitHub用户名）
git remote set-url origin https://github.com/YOUR_USERNAME/gemini-fullstack-langgraph-quickstart.git

# 验证远程仓库配置
git remote -v
```

#### 步骤3：推送到您的仓库

```powershell
# 推送所有提交到您的仓库
git push origin main
```

### 🔐 如果遇到认证问题

如果推送时遇到认证问题，您需要设置GitHub认证：

**方法1：使用Personal Access Token**
1. 访问 GitHub Settings → Developer settings → Personal access tokens
2. 生成新的token，选择 `repo` 权限
3. 推送时使用：
```powershell
git push https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/gemini-fullstack-langgraph-quickstart.git main
```

**方法2：使用GitHub CLI（如果已安装）**
```powershell
gh auth login
git push origin main
```

### 方法2：创建全新仓库

如果您想要完全独立的仓库：

#### 步骤1：在GitHub创建新仓库

1. 登录GitHub
2. 点击 **"+"** -> **"New repository"**
3. 设置仓库名称（如：`my-langgraph-research-app`）
4. 选择Public或Private
5. **不要**勾选"Initialize with README"
6. 点击 **"Create repository"**

#### 步骤2：更改远程仓库

```powershell
# 移除原来的远程仓库
git remote remove origin

# 添加您的新仓库（替换YOUR_USERNAME和REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 推送到新仓库
git branch -M main
git push -u origin main
```

## 🔐 GitHub认证设置

### 选项1：使用Personal Access Token（推荐）

1. **生成Token**：

   - 访问 GitHub Settings > Developer settings > Personal access tokens
   - 点击 "Generate new token"
   - 选择适当的权限（至少需要 `repo` 权限）
2. **使用Token**：

   ```powershell
   # 在推送时使用用户名和token
   git push https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/REPO_NAME.git
   ```

### 选项2：使用SSH密钥

1. **生成SSH密钥**：

   ```powershell
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
2. **添加到GitHub**：

   - 复制公钥内容：`cat ~/.ssh/id_ed25519.pub`
   - 在GitHub Settings > SSH and GPG keys中添加
3. **使用SSH URL**：

   ```powershell
   git remote set-url origin git@github.com:YOUR_USERNAME/REPO_NAME.git
   ```

## 📝 推荐的仓库结构

```
您的仓库/
├── README.md              # 项目主说明文档
├── STARTUP_GUIDE.md       # 启动指南（我们创建的）
├── GITHUB_SETUP.md        # 此文件
├── start-dev.ps1          # 增强版启动脚本
├── start-dev.bat          # 批处理启动脚本
├── debug-start.bat        # 调试启动脚本
├── frontend/              # React前端
├── backend/               # LangGraph后端
└── docs/                  # 额外文档（可选）
```

## 🔄 保持与原仓库同步（Fork方法）

如果使用Fork方法，您可以定期同步原仓库的更新：

```powershell
# 添加上游仓库
git remote add upstream https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart.git

# 获取上游更新
git fetch upstream

# 合并更新到您的main分支
git checkout main
git merge upstream/main

# 推送合并后的更新
git push origin main
```

## 🛠️ 自定义您的仓库

### 更新README.md

建议在README.md中添加：

- 您的改进和定制
- 安装和使用您增强版脚本的说明
- 遇到问题的解决方案
- 您的联系信息

### 创建发布标签

```powershell
# 创建版本标签
git tag -a v1.0 -m "Initial enhanced version with Windows startup scripts"
git push origin v1.0
```

## 🚨 注意事项

1. **API密钥安全**：

   - 永远不要将真实的API密钥提交到公共仓库
   - 使用 `.env` 文件并将其添加到 `.gitignore`
2. **许可证**：

   - 原项目使用Apache 2.0许可证
   - 确保您的修改符合许可证要求
3. **贡献回馈**：

   - 如果您的改进对其他人有用，考虑向原仓库提交Pull Request

## 📞 获取帮助

如果在设置过程中遇到问题：

1. 检查GitHub的[官方文档](https://docs.github.com/)
2. 确认您的Git配置：`git config --list`
3. 检查网络连接和防火墙设置
