# 项目文件整理方案

## 当前问题
根目录有50+个文件，混合了：
- 代码文件
- 文档报告
- 测试文件
- 旧代码
- 临时文件

## 整理方案

### 1. 保留在根目录的文件（核心文件）
```
✓ main.py                    # 后端入口
✓ requirements.txt           # Python依赖
✓ config.json                # 配置文件
✓ config.json.example        # 配置示例
✓ .env.example               # 环境变量示例
✓ .gitignore                 # Git配置
✓ README.md                  # 项目说明
✓ quick-start.ps1           # 快速启动脚本
✓ stop.ps1                  # 停止脚本
```

### 2. 移动到 docs/archives/ 的文档
```
→ docs/archives/reports/
  - API_SESSION_FIX_REPORT.md
  - API_SETUP.md
  - BACKEND_API_COMPLETION_REPORT.md
  - CHANGELOG.md
  - DEMO_VS_ELECTRON_COMPARISON.md
  - DEPLOYMENT.md
  - EXECUTION_GUIDE.md
  - FEATURE_COMPLETION_REPORT.md
  - FINAL_FIX_REPORT.md
  - PROJECT_COMPLETION_REPORT.md
  - PROJECT_SUMMARY.md
  - QUICKSTART.md
  - REMINDER_FEATURE_REPORT.md
  - SESSION_FIX_SUMMARY.md
  - 交付清单.md
```

### 3. 移动到 archive/ 的旧代码
```
→ archive/
  - demo/                    # 旧Demo
  - ui/                      # 旧GUI
  - modules/                 # 旧模块
  - utils/                   # 旧工具
  - rounds_generator.py      # 参考工具
```

### 4. 移动到 tests/ 的测试文件
```
→ tests/
  - test_api.py
  - test_api_comparison.py
  - test_api_routes.py
  - test_improved_gui.py
  - test_main.py
  - test_network.py
  - test_openai_api.py
  - test_startup.py
```

### 5. 移动数据库文件
```
→ data/
  - rehab_assistant.db
```

### 6. 删除无用文件
```
✗ nul                       # 空文件
✗ 微信图片_*.png            # 临时图片
```

## 整理后的目录结构
```
new/
├── main.py                    # 后端入口
├── requirements.txt           # Python依赖
├── config.json                # 配置文件
├── README.md                  # 项目说明
├── quick-start.ps1           # 快速启动
├── stop.ps1                  # 停止服务
│
├── backend/                   # 后端代码
│   ├── api/
│   ├── utils/
│   └── api_main.py
│
├── electron-app/              # Electron应用
│   ├── src/
│   ├── package.json
│   └── ...
│
├── ai_services/               # AI服务
│   ├── base_service.py
│   ├── deepseek_service.py
│   └── ...
│
├── database/                  # 数据库模型
│   └── models.py
│
├── knowledge_base/            # 知识库
│
├── data/                      # 数据文件（新建）
│   └── rehab_assistant.db
│
├── tests/                     # 测试文件
│   ├── test_api.py
│   └── ...
│
├── docs/                      # 文档
│   ├── 2025-01-23-康复科助手系统设计.md
│   ├── plans/
│   └── archives/              # 旧文档归档
│       ├── reports/
│       └── ...
│
└── archive/                   # 旧代码归档
    ├── demo/
    ├── ui/
    └── ...
```

## 执行步骤

1. 创建目录结构
2. 移动文件到对应目录
3. 删除无用文件
4. 更新 .gitignore
5. 更新 README.md

是否执行此整理方案？
