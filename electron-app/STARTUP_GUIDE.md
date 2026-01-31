# 🚀 应用启动指南

**更新日期**: 2025-01-23
**版本**: v1.0.0-electron

---

## 📋 启动前检查

### 环境要求
- ✅ Python 3.13+ (当前: 3.13.3)
- ✅ Node.js 18+ (已安装依赖)
- ✅ config.json (需要配置API密钥)

---

## 🎯 快速启动（3步）

### 步骤1: 启动Python后端服务

打开**第一个**终端窗口：

```bash
cd C:\Users\youda\Desktop\new
python main.py
```

**预期输出**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**如果报错** "ModuleNotFoundError":
```bash
pip install fastapi uvicorn sqlalchemy pydantic
```

---

### 步骤2: 启动Electron前端应用

等待后端启动完成后，打开**第二个**终端窗口：

```bash
cd C:\Users\youda\Desktop\new\electron-app
npm run dev
```

**预期输出**:
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help

  Preload script starting...
```

**Electron窗口应该自动打开** ✅

---

### 步骤3: 验证修复效果

#### ✅ 检查点1: Preload脚本加载
打开Electron应用后，在DevTools Console中应该**不出现**以下错误：
```
❌ Unable to load preload script
```

#### ✅ 检查点2: 患者列表显示
左侧患者列表应该正常显示，无以下错误：
```
❌ Uncaught (in promise) TypeError: patients.value is not iterable
```

#### ✅ 检查点3: 功能测试
- 点击"新建患者"按钮
- 填写患者信息
- 查看AI病程记录生成功能

---

## 🐛 故障排查

### 问题1: 后端启动失败

**错误**: `ModuleNotFoundError: No module named 'fastapi'`

**解决**:
```bash
pip install fastapi uvicorn sqlalchemy pydantic openai
```

---

### 问题2: 前端启动失败

**错误**: `command not found: npm`

**解决**: 安装Node.js从 https://nodejs.org/

---

### 问题3: Preload脚本仍然报错

**错误**: `Unable to load preload script`

**解决**: 清理并重新构建
```bash
cd C:\Users\youda\Desktop\new\electron-app
rmdir /s /q dist 2>nul
rmdir /s /q node_modules 2>nul
npm install
npm run dev
```

---

### 问题4: 患者列表为空

**原因**: 数据库中没有数据

**解决**: 在应用中点击"新建患者"按钮创建测试数据

---

## 📊 验证成功标志

当应用正常运行时，你应该看到：

### 后端终端
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 前端终端
```
VITE v5.0.0  ready in xxx ms
➜  Local:   http://localhost:5173/
Preload script starting...
```

### Electron窗口
- ✅ 窗口正常打开
- ✅ 三栏布局显示（左侧患者、中间工作区、右侧工具）
- ✅ DevTools Console无错误信息
- ✅ 可以点击按钮交互

---

## 🎉 下一步

### 测试通过后可以：
1. **功能测试**: 按照 `tests/manual_test_plan.md` 进行完整测试
2. **打包发布**: 运行 `npm run build:win` 生成Windows安装包
3. **日常使用**: 将快捷方式放到桌面方便启动

### 需要帮助？
查看文档:
- `README.md` - 快速开始
- `DEPLOYMENT.md` - 详细部署指南
- `tests/bug_fix_report.md` - 已修复的错误说明

---

**祝使用愉快！** 🏥✨
