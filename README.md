# 🏥 康复科助手 (Rehabilitation Assistant)

> 一款为中醫院康复科医生设计的AI辅助病历与事务管理系统

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-007AFF)](https://tomschimansky.github.io/customtkinter/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## ✨ 项目简介

康复科助手是一款专为中医院康复科医生设计的桌面应用程序，通过AI技术辅助医生完成病历书写、患者管理和事务提醒工作，提高工作效率，让医生有更多时间专注于患者治疗。

### 🎯 核心功能

- ✅ **AI病程记录生成** - 结合患者历史和AI智能生成符合规范的病程记录
- ✅ **智能提醒系统** - 自动提醒重要时间节点（如90天住院限制、检验复查等）
- ✅ **患者信息管理** - 从首次病程记录自动提取结构化患者信息
- ✅ **知识库辅助** - 集成专业医学知识库，提升记录质量
- ✅ **康复计划制定** - AI辅助制定个性化康复方案
- ✅ **iOS风格界面** - 现代化、美观、易用的用户界面

---

## 🎨 界面预览

<div align="center">
  <p>交互式界面演示（可在浏览器中打开查看）</p>
  <p>打开 <code>demo/index.html</code> 查看完整演示</p>
</div>

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- pip包管理器

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/chyyd/rehabilitation-assistant.git
cd rehabilitation-assistant
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置API密钥**

复制配置模板并填入您的API密钥：
```bash
cp config.json.example config.json
```

编辑 `config.json` 文件，填入您的真实API密钥：
```json
{
  "siliconflow": {
    "api_key": "你的硅基流动API密钥"
  },
  "ai_services": {
    "modelscope": {
      "api_key": "你的魔搭API密钥"
    },
    "deepseek": {
      "api_key": "你的DeepSeek API密钥"
    },
    "kimi": {
      "api_key": "你的Kimi API密钥"
    }
  }
}
```

**API密钥获取**：
- 硅基流动：https://siliconflow.cn（免费）
- 魔搭社区：https://modelscope.cn
- DeepSeek：https://platform.deepseek.com
- Kimi：https://platform.moonshot.cn

4. **启动应用**
```bash
python main.py
```

---

## 📋 查看界面演示

在实施前，可以先查看已完成的交互式HTML演示：

```bash
# 在浏览器中打开
demo/index.html
```

或者直接双击 `demo/index.html` 文件。

---

## 📚 文档

### 核心文档

- **[系统设计文档](docs/2025-01-23-康复科助手系统设计.md)** - 完整的系统架构和功能设计
- **[实施计划](docs/plans/2025-01-23-康复科助手完整实施计划.md)** - 详细的开发实施计划
- **[执行指南](EXECUTION_GUIDE.md)** - 在独立会话中执行的指南
- **[快速开始](QUICKSTART.md)** - 快速参考卡片

### 查看演示

1. 查看界面演示：打开 `demo/index.html`
2. 查看实施计划：阅读 `docs/plans/2025-01-23-康复科助手完整实施计划.md`
3. 开始实施：使用 `superpowers:executing-plans` 技能

---

## 🛠️ 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **GUI框架** | CustomTkinter | iOS风格桌面界面 |
| **数据库** | SQLAlchemy + SQLite | ORM和本地数据存储 |
| **向量数据库** | ChromaDB | 知识库语义检索 |
| **AI服务** | ModelScope/DeepSeek/Kimi | 病程记录生成 |
| **嵌入服务** | 硅基流动API | 文本向量化（免费）|
| **文档解析** | PyPDF/python-docx/ebooklib | 多格式文档支持 |

---

## 📊 项目进度

### 已完成 ✅

- [x] 需求分析与头脑风暴
- [x] 完整系统设计（25,000字）
- [x] 交互式界面演示（HTML/CSS/JS）
- [x] 详细实施计划（8大任务）
- [x] 执行指南和快速开始文档

### 待实施 🚧

- [ ] Python后端开发
- [ ] CustomTkinter GUI实现
- [ ] AI服务集成
- [ ] ChromaDB知识库实现
- [ ] 单元测试和集成测试
- [ ] 用户文档完善

**项目状态**：设计完成，待实施

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 👨‍⚕️ 作者

**于友达** - 中医院康复科医生

---

## 🙏 致谢

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 现代化的Python GUI框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包和ORM
- [ChromaDB](https://www.trychroma.com/) - 开源嵌入数据库
- [硅基流动](https://siliconflow.cn/) - 免费的AI嵌入服务

---

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub Issues: [提交问题](https://github.com/chyyd/rehabilitation-assistant/issues)

---

## ⭐ Star History

如果这个项目对您有帮助，请给它一个星标！

---

**🎉 让AI助力医疗康复工作！**
