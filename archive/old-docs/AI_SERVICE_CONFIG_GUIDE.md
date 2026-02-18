# AI服务配置功能使用指南

## ✅ 新增功能

### 1. 支持的AI服务
- **DeepSeek** - 推理能力强，逻辑清晰
- **ModelScope (魔搭)** - 价格低，中文能力强
- **Kimi (月之暗面)** - 长文本支持好
- **自定义服务** - 支持任何兼容OpenAI API的服务

### 2. 支持的Embedding服务（知识库）
- **硅基流动** - 默认推荐
- **ModelScope** - 可复用ModelScope API密钥
- **自定义服务** - 支持任何兼容服务

### 3. 新增功能
- ✅ 连接测试按钮 - 验证配置是否正确
- ✅ 动态配置界面 - 根据选择显示对应配置
- ✅ 自动默认值 - 切换服务时自动填充推荐配置
- ✅ 独立参数存储 - 每个服务的配置分开保存

## 🚀 启动步骤

### 方法1：使用PowerShell脚本（推荐）

```powershell
# 快速启动
.\quick-start.ps1

# 或使用交互式菜单
.\start.ps1
```

### 方法2：手动启动

```powershell
# 1. 确保没有旧进程
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"

# 2. 启动后端
cd C:\Users\youda\Desktop\new
python main.py

# 3. 启动前端（新窗口）
cd C:\Users\youda\Desktop\new\electron-app
npm run dev
```

## 📝 配置步骤

### 配置AI服务

1. **打开设置**
   - 点击右上角"设置"按钮
   - 选择"AI服务"标签

2. **选择默认服务**
   - 从下拉菜单选择：DeepSeek / ModelScope / Kimi / 自定义

3. **填写配置**
   - **API密钥**：从对应平台获取
   - **Base URL**：自动填充默认值，可修改
   - **模型名称**：自动填充推荐模型，可修改

4. **测试连接**
   - 点击"测试连接"按钮
   - 等待验证结果
   - 成功会显示："XXX连接测试成功！"

### 配置Embedding服务（可选）

1. **选择Embedding服务**
   - 硅基流动（推荐）
   - ModelScope
   - 自定义

2. **填写配置**
   - API密钥
   - Base URL
   - 模型名称

3. **测试连接**
   - 点击"测试Embedding"按钮

## 🔑 获取API密钥

### DeepSeek
1. 访问：https://platform.deepseek.com/
2. 注册/登录账号
3. 进入API Keys页面
4. 创建新的API密钥

### ModelScope (魔搭)
1. 访问：https://modelscope.cn/
2. 注册/登录账号
3. 进入个人中心 → API令牌
4. 创建新的访问令牌

### Kimi (月之暗面)
1. 访问：https://platform.moonshot.cn/
2. 注册/登录账号
3. 进入API Keys页面
4. 创建新的API密钥

### 硅基流动 (Embedding)
1. 访问：https://siliconflow.cn/
2. 注册/登录账号
3. 进入API密钥管理
4. 创建新的API密钥

## 🧪 测试API端点

### 验证端点可用

在浏览器中访问：http://127.0.0.1:8000/docs

应该能看到Swagger文档，包含：
- `POST /api/ai/test` - 测试AI服务
- `POST /api/ai/test-embedding` - 测试Embedding服务

### 使用测试脚本

```bash
python test-api-endpoint.py
```

## ⚠️ 常见问题

### 问题1：测试连接显示404

**原因**：有旧的后端进程在运行

**解决**：
```powershell
# 停止所有Python进程
powershell -Command "Get-Process python | Stop-Process -Force"

# 重新启动后端
python main.py
```

### 问题2：无法连接到后端

**检查项**：
1. 后端是否已启动（应该看到 "Uvicorn running on http://127.0.0.1:8000"）
2. 端口8000是否被占用
3. 防火墙是否阻止连接

**解决**：
```powershell
# 检查端口占用
netstat -ano | findstr :8000

# 如果被占用，找到进程ID并终止
taskkill /PID <进程ID> /F
```

### 问题3：配置保存后丢失

**当前版本**：配置保存在浏览器的localStorage中

**注意**：
- 清除浏览器数据会导致配置丢失
- 建议记录好API密钥

**未来改进**：配置将保存到后端数据库

## 📊 推荐配置

### 经济实惠方案
- **AI服务**：ModelScope (DeepSeek-V3)
- **Embedding**：硅基流动 (BAAI/bge-large-zh-v1.5)
- **优势**：价格低，中文能力强

### 高性能方案
- **AI服务**：DeepSeek (deepseek-chat)
- **Embedding**：硅基流动 (BAAI/bge-large-zh-v1.5)
- **优势**：推理能力强，逻辑清晰

### 长文本方案
- **AI服务**：Kimi (moonshot-v1-8k)
- **Embedding**：ModelScope
- **优势**：支持长文本输入

## 🎯 完成清单

使用前请确认：
- [ ] 后端服务已启动（http://127.0.0.1:8000）
- [ ] 前端应用已打开
- [ ] 已获取API密钥
- [ ] 已测试连接成功
- [ ] 配置已保存

## 📞 技术支持

如遇问题，请提供：
1. 错误截图
2. 浏览器控制台日志（F12）
3. 后端启动日志

---

**最后更新**：2026-01-31
**版本**：v1.0.0
