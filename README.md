# 康复科助手

> 基于Electron + Python FastAPI的康复科病历与事务管理系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-electron-green.svg)](https://github.com)

## 项目简介

康复科助手是一款专为中医院康复科设计的智能病历管理桌面应用，通过AI技术辅助医生进行病程记录生成、患者信息管理和智能提醒。

### 核心特性

- ✨ **AI智能生成** - 结合AI自动生成符合规范的病程记录
- 📋 **智能提醒系统** - 自动提醒重要时间节点（90天限制、阶段小结等）
- 👤 **患者信息管理** - 从首次病程记录自动提取结构化信息
- 📚 **知识库辅助** - 集成专业医学知识库，提升记录质量
- 🏥 **康复计划制定** - AI辅助制定个性化康复方案
- 📝 **模板管理** - AI提取常用语句，智能分类管理
- ✍️ **智能签名** - 根据记录类型自动匹配医师签名
- 💾 **离线优先** - 核心功能本地运行，数据安全可控

## 技术栈

### 前端
- **Electron 28** - 跨平台桌面应用框架
- **Vue 3.4** - 渐进式JavaScript框架
- **TypeScript 5.3** - 类型安全的JavaScript超集
- **Element Plus 2.5** - Vue 3 UI组件库
- **Pinia 2.1** - Vue状态管理
- **Vite 5.0** - 快速构建工具

### 后端
- **Python 3.13+** - 编程语言
- **FastAPI 0.116** - 现代化Python Web框架
- **SQLAlchemy 2.0** - ORM数据库工具
- **SQLite 3** - 轻量级数据库
- **Uvicorn** - ASGI服务器

### AI服务
- **ModelScope (魔搭)** - 主要AI服务提供商（DeepSeek-V3）
- **DeepSeek** - 备用AI服务
- **Kimi** - 备用AI服务
- **硅基流动** - Embedding API服务
- **ChromaDB** - 向量数据库

## 快速开始

### 环境要求

- Python 3.13+
- Node.js 18+
- npm 9+

### 一键启动

Windows系统推荐使用PowerShell启动脚本：

```powershell
# 快速启动（新窗口模式）
.\quick-start.ps1

# 完整启动（交互式菜单）
.\start.ps1

# 停止所有服务
.\stop.ps1
```

### 手动启动

#### 1. 安装依赖

```bash
# Python后端依赖
pip install -r requirements.txt

# Electron前端依赖
cd electron-app
npm install
cd ..
```

#### 2. 配置

复制配置文件模板并填写API密钥：

```bash
# Windows
copy config.json.example config.json

# Linux/macOS
cp config.json.example config.json
```

编辑 `config.json`，填入您的API密钥（详见 [配置说明](#配置说明)）。

#### 3. 启动应用

**方式1：启动Python后端服务（终端1）**
```bash
python main.py
```

后端服务将启动在 http://127.0.0.1:8000

API文档: http://127.0.0.1:8000/docs

**方式2：启动Electron前端（终端2）**
```bash
cd electron-app
npm run dev
```

应用窗口将自动打开。

## 使用指南

### 创建新患者

1. 点击右上角 "新患者" 按钮
2. 输入住院号
3. 粘贴首次病程记录
4. 确认AI提取的患者信息
5. 保存患者档案

### 生成病程记录

1. 从左侧患者列表选择患者
2. 选择记录类型（住院医师/主治医师/主任医师查房）
3. 在 "当日情况" 文本框输入今日情况
4. 点击 "AI生成" 按钮
5. 查看并微调生成的内容（签名已自动添加）
6. 点击 "保存" 保存病程记录
7. （可选）点击 "导出txt" 导出记录

### 智能签名系统

签名根据记录类型自动匹配医师信息：

- **住院医师查房** → 单行签名（住院医师）
- **主治医师查房** → 双行签名（住院医师 + 主治医师）
- **主任医师查房** → 双行签名（住院医师 + 主任医师）

在设置中配置医师姓名即可自动应用。

### 模板管理

1. 打开设置 → 模板管理
2. 上传包含病程记录的 .md/.txt 文件
3. 点击"AI分析提取"
4. Python预处理提取高频语句（降97%成本）
5. AI优化并分类语句
6. 编辑提取的模板
7. 批量保存到模板库

### 查看提醒

- 启动应用自动加载今日提醒
- 左栏患者卡片显示提醒数量和优先级
- 点击卡片查看具体提醒
- 完成后点击"完成"按钮标记

## 项目结构

```
new/
├── main.py                    # 后端启动器
├── requirements.txt           # Python依赖
├── config.json.example        # 配置示例
├── quick-start.ps1           # 快速启动脚本
├── start.ps1                  # 完整启动脚本
├── stop.ps1                   # 停止服务脚本
│
├── backend/                   # Python后端API
│   ├── api_main.py           # FastAPI应用入口
│   └── api/routes/           # API路由
│       ├── patients.py       # 患者管理
│       ├── notes.py          # 病程记录
│       ├── reminders.py      # 提醒事项
│       ├── templates.py      # 模板管理
│       ├── rehab_plans.py    # 康复计划
│       └── ai.py             # AI接口
│
├── electron-app/              # Electron前端
│   ├── electron/             # Electron主进程
│   ├── preload/              # Preload脚本
│   ├── src/                  # Vue源码
│   │   ├── components/       # Vue组件
│   │   │   ├── PatientList.vue
│   │   │   ├── Workspace.vue
│   │   │   ├── NoteGenerationCard.vue
│   │   │   ├── RehabPlanCard.vue
│   │   │   ├── TaskCard.vue
│   │   │   ├── QuickTools.vue
│   │   │   ├── PatientInfoCard.vue
│   │   │   └── SettingsDialog.vue
│   │   ├── stores/           # Pinia状态管理
│   │   │   ├── patient.ts
│   │   │   └── note.ts
│   │   └── utils/            # 工具函数
│   │       └── eventBus.ts
│   └── package.json
│
├── ai_services/               # AI服务模块
│   ├── base_service.py       # AI服务基类
│   ├── deepseek_service.py   # DeepSeek实现
│   ├── modelscope_service.py # ModelScope实现
│   ├── kimi_service.py       # Kimi实现
│   └── service_manager.py    # 服务管理器
│
├── database/                  # 数据库模型
│   └── models.py             # SQLAlchemy模型
│
├── backend/utils/             # 后端工具
│   └── text_processor.py     # 文本预处理
│
├── knowledge_base/            # 知识库管理
│   └── files/                # 知识库文档
│
├── data/                      # 数据文件
│   └── rehab_assistant.db    # SQLite数据库
│
├── tests/                     # 测试文件
│   └── test_*.py
│
├── docs/                      # 文档
│   ├── 2025-01-23-康复科助手系统设计.md
│   ├── plans/                # 开发计划
│   └── archives/             # 历史文档归档
│
└── archive/                   # 旧代码归档
    ├── demo/                 # 旧Demo
    ├── ui/                   # 旧GUI
    └── modules/              # 旧模块
```

## 打包

### Windows打包

```bash
cd electron-app
npm run build:win
```

安装包将在 `electron-app/dist` 目录生成：
- `康复科助手 Setup 1.0.0.exe`

### 其他平台

```bash
# macOS
npm run build:mac

# Linux
npm run build:linux
```

## 配置说明

### AI服务配置

支持多个AI服务提供商：

1. **ModelScope (魔搭)** - 推荐
   - 注册: https://modelscope.cn/
   - 模型: deepseek-ai/DeepSeek-V3
   - 价格低，中文能力强

2. **DeepSeek**
   - 注册: https://platform.deepseek.com/
   - 模型: deepseek-chat
   - 推理能力强，逻辑清晰

3. **Kimi (月之暗面)**
   - 注册: https://platform.moonshot.cn/
   - 模型: moonshot-v1-8k
   - 长文本支持好

### 医师信息配置

在应用设置中配置：
- 住院医师姓名
- 主治医师姓名
- 主任医师姓名

签名会根据记录类型自动匹配。

### 知识库配置

将医学文档（PDF/EPUB/Word/TXT）放入 `knowledge_base/files/` 目录，应用会自动向量化。

## 数据备份

重要数据位置：
- 数据库: `data/rehab_assistant.db`
- 配置文件: `config.json`
- 知识库向量: `knowledge_base/data/`

备份命令（Windows）:
```bash
# 备份数据库
copy data\rehab_assistant.db backup\rehab_assistant_%date%.db

# 备份知识库
xcopy knowledge_base\data backup\knowledge_data_%date%\ /E /I
```

## 新增功能（v1.0）

### 模板智能管理
- Python预处理提取高频语句（降97% token消耗）
- AI优化语句规范化
- 自动分类（7种类别）
- 批量导入导出

### 智能签名系统
- 根据记录类型自动匹配
- 支持多医师签名
- 符合医疗文书规范

### 快速启动脚本
- PowerShell一键启动
- 自动检测环境
- 新窗口/当前窗口模式

## 故障排除

### 问题1: 后端服务启动失败

**症状:** 运行 `python main.py` 报错

**解决方案:**
1. 确认Python版本 >= 3.13
2. 重新安装依赖: `pip install -r requirements.txt`
3. 检查config.json格式是否正确
4. 查看错误日志

### 问题2: Electron前端启动失败

**症状:** 运行 `npm run dev` 报错

**解决方案:**
1. 确认Node.js版本 >= 18
2. 删除node_modules重新安装: `rm -rf node_modules && npm install`
3. 检查端口5173是否被占用
4. 查看浏览器控制台错误

### 问题3: AI生成失败

**症状:** 点击 "AI生成" 无响应或报错

**解决方案:**
1. 检查API密钥是否正确配置
2. 确认网络连接正常
3. 尝试切换备用AI服务
4. 查看后端控制台错误日志

### 问题4: 数据库文件未找到

**症状:** 启动报错找不到数据库

**解决方案:**
1. 确认数据库文件位置: `data/rehab_assistant.db`
2. 检查data目录是否存在
3. 如需迁移旧数据库，从根目录移动到data/

## 开发指南

### 添加新的API路由

1. 在 `backend/api/routes/` 创建新文件
2. 定义FastAPI路由和Pydantic模型
3. 在 `backend/api_main.py` 注册路由
4. 重启后端服务

### 添加新的Vue组件

1. 在 `electron-app/src/components/` 创建 `.vue` 文件
2. 使用 `<script setup lang="ts">` 语法
3. 遵循Element Plus组件规范
4. 在需要的地方导入组件

### 代码风格

- Python: 遵循PEP 8规范
- TypeScript: 使用ESLint + Prettier
- Vue 3: 使用Composition API

## 文档

- [部署指南](docs/archives/reports/DEPLOYMENT.md) - 详细的部署和安装说明
- [API文档](http://127.0.0.1:8000/docs) - FastAPI自动生成的Swagger文档
- [测试报告](docs/archives/reports/) - 历史测试报告

## 更新日志

### v1.0.0 (2026-01-31)
- ✅ 完成Electron桌面应用开发
- ✅ AI智能病程记录生成
- ✅ 智能提醒系统
- ✅ 模板管理功能
- ✅ 智能签名系统
- ✅ 快速启动脚本
- ✅ 项目文件整理优化

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 致谢

感谢以下开源项目：

- [Electron](https://www.electronjs.org/)
- [Vue.js](https://vuejs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Element Plus](https://element-plus.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [DeepSeek](https://www.deepseek.com/)
- [ModelScope](https://modelscope.cn/)

---

**项目状态**: ✅ v1.0.0 已完成

**最后更新**: 2026-01-31
