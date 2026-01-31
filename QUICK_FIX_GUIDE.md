# 快速修复指南 - 模板管理500错误

## 🐛 问题描述

**错误**：`POST /api/templates/extract-phrases 500 (Internal Server Error)`

**原因**：后端运行的是旧代码，未加载修复后的代码

## ✅ 解决方案（3选1）

### 方案1：使用自动重启脚本（推荐）

```powershell
# 运行重启脚本
.\restart-backend.ps1
```

**优点**：
- 自动停止旧进程
- 自动启动新进程
- 自动验证端点

---

### 方案2：使用诊断工具

```powershell
# 运行诊断工具
python diagnose-backend.py
```

**功能**：
- ✅ 检查代码是否已修复
- ✅ 检查Python进程
- ✅ 验证API端点
- ✅ 提供修复建议

---

### 方案3：手动修复

#### 步骤1：停止所有Python进程

```powershell
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"
```

#### 步骤2：等待2秒

```powershell
Start-Sleep -Seconds 2
```

#### 步骤3：启动后端

```powershell
cd C:\Users\youda\Desktop\new
python main.py
```

#### 步骤4：验证端点

打开浏览器访问：http://127.0.0.1:8000/docs

确认可以看到：
- `POST /api/templates/extract-phrases`
- `POST /api/ai/test`
- `POST /api/ai/test-embedding`

---

## 🔍 验证修复

### 测试步骤

1. **打开应用**
   ```
   cd C:\Users\youda\Desktop\new\electron-app
   npm run dev
   ```

2. **进入模板管理**
   - 设置 → 模板管理

3. **上传测试文件**
   - 选择一个 .md 或 .txt 文件
   - 点击"一键分析所有文件"

4. **检查结果**
   - ✅ 应该看到"分析完成"提示
   - ✅ 显示提取的语句数量
   - ✅ 可以编辑和保存模板

### 预期结果

```
✅ 分析完成！成功 1 个文件，失败 0 个文件，共提取 25 条语句
```

---

## ⚠️ 常见问题

### 问题1：仍然报500错误

**原因**：后端没有完全重启

**解决**：
```powershell
# 强制停止所有Python进程
taskkill /F /IM python.exe /T

# 等待5秒
timeout /t 5

# 重新启动
python main.py
```

### 问题2：找不到 diagnose-backend.py

**原因**：文件不在当前目录

**解决**：
```powershell
cd C:\Users\youda\Desktop\new
python diagnose-backend.py
```

### 问题3：PowerShell禁止运行脚本

**原因**：执行策略限制

**解决**：
```powershell
# 临时允许脚本运行
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 然后运行脚本
.\restart-backend.ps1
```

---

## 📋 修复清单

使用前请确认：

- [ ] 代码已修复（`get_service()` 而非 `get_default_service()`）
- [ ] 所有Python进程已停止
- [ ] 后端服务已重新启动
- [ ] API端点可以访问（http://127.0.0.1:8000/docs）
- [ ] 前端应用已刷新

---

## 🎯 快速命令

复制粘贴以下命令：

```powershell
# 一键修复
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force; Start-Sleep -Seconds 2; cd 'C:\Users\youda\Desktop\new'; python main.py"
```

---

## 📞 技术支持

如果问题仍然存在：

1. 运行诊断工具：`python diagnose-backend.py`
2. 查看后端控制台错误日志
3. 查看浏览器控制台（F12）错误日志
4. 提供错误截图和日志

---

**最后更新**：2026-01-31
**版本**：v1.0.1
**状态**：✅ 已修复
