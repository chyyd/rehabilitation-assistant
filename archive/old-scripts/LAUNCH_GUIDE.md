# 康复科助手 - 生产环境启动指南

## 📋 启动脚本说明

### ⚡ 快速启动

| 脚本 | 功能 | 窗口显示 |
|------|------|---------|
| `start-all.ps1` | **一键启动前后端** | ✅ 仅显示启动界面 |
| `stop-all.ps1` | **一键停止所有服务** | ✅ 显示停止界面 |

### 🔧 单独控制

| 脚本 | 功能 | 窗口显示 |
|------|------|---------|
| `start-backend.ps1` | 仅启动后端服务 | ❌ 完全隐藏 |
| `start-frontend.ps1` | 仅启动前端应用 | ✅ 仅显示启动界面 |
| `stop-backend.ps1` | 停止后端服务 | ✅ 显示停止界面 |
| `stop-frontend.ps1` | 停止前端应用 | ✅ 显示停止界面 |

---

## 🚀 使用方法

### 方式一：一键启动（推荐）

```powershell
# 在项目根目录右键 -> "在终端中打开"
.\start-all.ps1
```

**特点：**
- ✅ 自动启动后端和前端
- ✅ 后端完全隐藏在后台运行
- ✅ Electron 应用窗口正常显示
- ✅ 启动窗口可随时关闭

### 方式二：分开启动

```powershell
# 终端1: 启动后端（隐藏窗口）
.\start-backend.ps1

# 终端2: 启动前端
.\start-frontend.ps1
```

---

## 🛑 停止服务

### 一键停止（推荐）

```powershell
.\stop-all.ps1
```

### 分开停止

```powershell
# 停止后端
.\stop-backend.ps1

# 停止前端
.\stop-frontend.ps1
```

---

## 📊 服务信息

| 服务 | 地址 | 说明 |
|------|------|------|
| **后端 API** | http://127.0.0.1:8000 | FastAPI 服务 |
| **API 文档** | http://127.0.0.1:8000/docs | Swagger UI |
| **前端应用** | Electron 窗口 | 桌面应用 |

---

## 🔍 进程管理

### 查看运行状态

```powershell
# 查看后端进程
Get-Process python | Where-Object { $_.CommandLine -like "*uvicorn*" }

# 查看前端进程
Get-Process electron
Get-Process node | Where-Object { $_.CommandLine -like "*vite*" }
```

### PID 文件

进程 ID 会自动保存到以下文件：
- `.backend.pid` - 后端进程 ID
- `.frontend.pid` - 前端进程 ID

停止脚本会自动读取这些文件来停止对应进程。

---

## ⚙️ 配置

### API 密钥配置

编辑 `config.json`：

```json
{
  "ai_services": {
    "modelscope": {
      "api_key": "你的密钥",
      "model": "Qwen2.5-72B-Instruct"
    }
  }
}
```

### 医师信息

在 `config.json` 中修改 `doctors` 部分。

---

## 🐛 故障排除

### 后端无法启动

1. **检查 Python 环境**
   ```powershell
   python --version
   # 需要 Python 3.13+
   ```

2. **检查依赖**
   ```powershell
   pip install -r requirements.txt
   ```

3. **检查端口占用**
   ```powershell
   netstat -ano | findstr :8000
   ```

### 前端无法启动

1. **检查 Node.js 环境**
   ```powershell
   node --version
   # 需要 Node.js 18+
   ```

2. **检查依赖**
   ```powershell
   cd electron-app
   npm install
   ```

### 强制停止服务

如果脚本无法停止，使用任务管理器：
- 结束 `python.exe` 进程（后端）
- 结束 `electron.exe` 和 `node.exe` 进程（前端）

---

## 📝 日志

日志文件保存在 `logs/` 目录：
- `backend_YYYYMMDD_HHmmss.log` - 后端日志

---

## 🔐 安全提示

- **不要** 将 `config.json` 提交到版本控制
- **不要** 在公开场合分享 API 密钥
- **建议** 使用 `.env` 文件管理敏感信息

---

## 💡 提示

1. **首次启动** 可能需要安装依赖，请耐心等待
2. **后端服务** 完全在后台运行，不会显示窗口
3. **前端应用** 会打开 Electron 窗口，启动窗口可关闭
4. 如需重启，先运行停止脚本，再运行启动脚本

---

## 📞 支持

如遇问题，请检查：
1. Python 和 Node.js 版本是否满足要求
2. 依赖包是否正确安装
3. 端口 8000 和 5173 是否被占用
4. `config.json` 配置是否正确

---

**祝使用愉快！** 🎉
