# 部署指南

本文档详细说明康复科助手在不同环境下的部署方法。

## 目录

- [开发环境部署](#开发环境部署)
- [生产环境打包](#生产环境打包)
- [服务器部署](#服务器部署)
- [数据备份与恢复](#数据备份与恢复)
- [常见问题](#常见问题)

---

## 开发环境部署

### Windows

#### 1. 安装Python

1. 访问 https://www.python.org/downloads/
2. 下载Python 3.13+ Windows installer
3. 运行安装程序，**务必勾选 "Add Python to PATH"**
4. 验证安装:
   ```bash
   python --version
   # 应显示: Python 3.13.x
   ```

#### 2. 安装Node.js

1. 访问 https://nodejs.org/
2. 下载LTS版本（推荐v22+）
3. 运行安装程序
4. 验证安装:
   ```bash
   node --version
   npm --version
   ```

#### 3. 克隆项目

```bash
git clone https://github.com/yourusername/rehabilitation_assistant.git
cd rehabilitation_assistant
```

#### 4. 创建配置文件

```bash
copy config.json.example config.json
notepad config.json
```

填写您的API密钥。

#### 5. 安装依赖

```bash
# Python依赖
pip install -r requirements.txt

# Electron前端依赖
cd electron-app
npm install
cd ..
```

#### 6. 启动开发服务

**终端1 - 启动Python后端:**
```bash
python main.py
```

**终端2 - 启动Electron前端:**
```bash
cd electron-app
npm run dev
```

### macOS

#### 1. 使用Homebrew安装

```bash
# 安装Python
brew install python@3.13

# 安装Node.js
brew install node

# 验证安装
python3 --version
node --version
```

#### 2. 克隆并配置

```bash
git clone https://github.com/yourusername/rehabilitation_assistant.git
cd rehabilitation_assistant
cp config.json.example config.json
# 编辑config.json
```

#### 3. 安装依赖

```bash
pip3 install -r requirements.txt
cd electron-app
npm install
cd ..
```

#### 4. 启动服务

```bash
# 终端1
python3 main.py

# 终端2
cd electron-app
npm run dev
```

### Linux (Ubuntu/Debian)

#### 1. 安装系统依赖

```bash
# 更新包管理器
sudo apt update

# 安装Python
sudo apt install python3 python3-pip python3-venv

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# 验证安装
python3 --version
node --version
```

#### 2. 克隆并配置

```bash
git clone https://github.com/yourusername/rehabilitation_assistant.git
cd rehabilitation_assistant
cp config.json.example config.json
# 编辑config.json
nano config.json
```

#### 3. 安装依赖

```bash
pip3 install -r requirements.txt
cd electron-app
npm install
cd ..
```

#### 4. 启动服务

```bash
# 终端1
python3 main.py

# 终端2
cd electron-app
npm run dev
```

---

## 生产环境打包

### Windows打包

#### 1. 准备打包环境

```bash
cd electron-app
npm install
```

#### 2. 执行打包

```bash
npm run build:win
```

#### 3. 查看输出

打包完成后，安装包位于:
```
electron-app/dist/康复科助手 Setup 1.0.0.exe
```

#### 4. 安装和运行

1. 双击 `康复科助手 Setup 1.0.0.exe`
2. 选择安装目录
3. 完成安装
4. 启动应用前需要先启动Python后端服务

### macOS打包

#### 1. 准备环境

```bash
# 安装Xcode命令行工具
xcode-select --install

# 进入项目目录
cd electron-app
npm install
```

#### 2. 执行打包

```bash
npm run build:mac
```

#### 3. 输出位置

```
electron-app/dist/康复科助手-1.0.0.dmg
```

#### 4. 签名和公证（发布到App Store需要）

```bash
# 导入证书
security import /path/to/cert.p12 -k ~/Library/Keychains/login.keychain

# 修改electron-builder.json添加签名配置
# "mac": {
#   "identity": "Developer ID Application: Your Name",
#   "hardenedRuntime": true
# }
```

### Linux打包

```bash
cd electron-app
npm install
npm run build:linux
```

输出:
```
electron-app/dist/康复科助手-1.0.0.AppImage
```

---

## 服务器部署

### 使用Docker部署

#### 1. 创建Dockerfile

**Dockerfile (Python后端):**
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "main.py"]
```

#### 2. 构建镜像

```bash
docker build -t rehab-assistant-backend .
```

#### 3. 运行容器

```bash
docker run -d \
  --name rehab-backend \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  rehab-assistant-backend
```

### 使用systemd服务（Linux）

#### 1. 创建服务文件

```bash
sudo nano /etc/systemd/system/rehab-assistant.service
```

#### 2. 服务配置

```ini
[Unit]
Description=康复科助手后端服务
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/rehabilitation_assistant
ExecStart=/usr/bin/python3 /path/to/rehabilitation_assistant/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 3. 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable rehab-assistant
sudo systemctl start rehab-assistant
sudo systemctl status rehab-assistant
```

---

## 数据备份与恢复

### 数据库备份

#### 自动备份脚本 (Windows)

**backup.bat:**
```batch
@echo off
set BACKUP_DIR=backup
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%

if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

echo 正在备份数据库...
copy rehab_assistant.db %BACKUP_DIR%\rehab_assistant_%TIMESTAMP%.db

echo 正在备份配置文件...
copy config.json %BACKUP_DIR%\config_%TIMESTAMP%.json

echo 正在备份知识库...
xcopy knowledge_base\data %BACKUP_DIR%\knowledge_data_%TIMESTAMP%\ /E /I /Y

echo 备份完成！
pause
```

#### 设置定时备份（Windows任务计划程序）

1. 打开 "任务计划程序"
2. 创建基本任务
3. 触发器: 每天 02:00
4. 操作: 启动程序 `backup.bat`

### 数据库恢复

```bash
# 停止应用
# 备份当前数据库
copy rehab_assistant.db rehab_assistant.db.backup

# 恢复备份
copy backup\rehab_assistant_20250123.db rehab_assistant.db

# 重启应用
python main.py
```

### 知识库迁移

```bash
# 导出知识库
xcopy knowledge_base\data backup\knowledge_export\ /E /I

# 导入知识库
xcopy backup\knowledge_export\ knowledge_base\data\ /E /I
```

---

## 性能优化

### 数据库优化

```python
# 定期VACUUM (SQLite)
import sqlite3
conn = sqlite3.connect('rehab_assistant.db')
conn.execute('VACUUM')
conn.close()

# 分析并重建索引
conn.execute('ANALYZE')
conn.execute('REINDEX')
```

### 应用优化

1. **减少启动时间**
   - 延迟加载非核心模块
   - 缓存常用数据

2. **内存优化**
   - 定期清理缓存
   - 限制患者列表加载数量

3. **网络优化**
   - 使用API响应缓存
   - 批量请求数据

---

## 常见问题

### Q1: 打包后应用无法启动

**A:** 检查以下几点:
1. 确认Python后端服务已启动
2. 检查防火墙是否阻止连接
3. 查看应用日志文件

### Q2: 数据库文件损坏

**A:** 尝试恢复:
```bash
# 检查数据库完整性
sqlite3 rehab_assistant.db "PRAGMA integrity_check;"

# 如果损坏，从备份恢复
```

### Q3: AI服务超时

**A:**
1. 检查网络连接
2. 增加超时时间配置
3. 切换备用AI服务

### Q4: 知识库检索慢

**A:**
1. 减少知识库文档数量
2. 调整chunk_size参数
3. 考虑使用更快的embedding模型

---

## 更新与升级

### 自动更新配置

修改 `electron-builder.json`:

```json
{
  "publish": {
    "provider": "github",
    "owner": "yourusername",
    "repo": "rehabilitation_assistant"
  }
}
```

### 手动更新流程

1. 备份数据
2. 下载新版本
3. 停止旧版本
4. 替换应用文件
5. 保留配置文件和数据库
6. 启动新版本

---

## 安全建议

1. **API密钥管理**
   - 不要将API密钥提交到版本控制
   - 定期轮换API密钥
   - 使用环境变量存储敏感信息

2. **数据库安全**
   - 定期备份数据库
   - 限制数据库文件权限
   - 考虑使用加密数据库

3. **网络安全**
   - 后端服务仅监听127.0.0.1
   - 使用HTTPS进行外部通信
   - 实施请求速率限制

---

## 监控与日志

### 日志位置

- Python后端: 控制台输出
- Electron前端: 开发者工具Console
- 数据库日志: `rehab_assistant.db-journal`

### 日志级别

- DEBUG: 详细调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息

---

## 许可证

MIT License

---

**文档版本**: 1.0.0
**最后更新**: 2025-01-23
