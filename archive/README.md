# 归档目录说明

本目录包含项目开发过程中创建的旧版本脚本和文档，已不再使用但保留供参考。

---

## 📁 old-scripts/

旧版本的启动和停止脚本，已被新的自动化脚本替代。

### 已废弃的脚本：
- `start.ps1` / `stop.ps1` - 旧版一键启动/停止脚本
- `start-all.ps1` / `stop-all.ps1` - 旧版本（包含用户交互提示）
- `start-backend.ps1` / `start-frontend.ps1` - 旧版单独启动脚本
- `stop-backend.ps1` / `stop-frontend.ps1` - 旧版单独停止脚本
- `quick-start.ps1` - 快速启动脚本
- `restart-backend.ps1` - 重启后端脚本
- `restart-clean.bat` / `stop-services.bat` - BAT批处理脚本
- `fix-scripts.ps1` - 临时修复脚本
- `test-start.ps1` - 测试脚本

### 替代的新脚本：
✅ `launch-all.ps1` - 一键启动（推荐）
✅ `stop-all-auto.ps1` - 一键停止
✅ `start-backend-auto.ps1` - 单独启动后端
✅ `start-frontend-auto.ps1` - 单独启动前端
✅ `生产环境启动.bat` - 菜单式启动器

---

## 📁 old-docs/

开发过程中的技术文档和更新说明。

### 功能开发文档：
- `AI_SERVICE_CONFIG_GUIDE.md` - AI服务配置指南
- `MULTI_FILE_UPLOAD_FEATURE.md` - 多文件上传功能说明
- `TEMPLATE_MANAGER_UPDATE.md` - 模板管理器更新说明
- `UI_UPDATE_PROGRESS_FEEDBACK.md` - UI更新进度反馈

### Bug修复文档：
- `BUG_FIX_GET_SERVICE.md` - 获取服务bug修复
- `QUICK_FIX_GUIDE.md` - 快速修复指南

### 已废弃的使用说明：
- `LAUNCH_GUIDE.md` - 英文启动指南（已被 `启动说明.md` 替代）
- `生产环境说明.md` - 旧版生产环境说明

---

## 🗑️ 清理时间

**归档日期：** 2026-02-02

**原因：** 项目根目录脚本文件过多，整理后只保留最新的自动化脚本。

---

## ⚠️ 注意

这些文件已不再维护，仅供参考。如需启动项目，请使用根目录下的最新脚本。

**推荐使用：**
```powershell
# 一键启动
.\launch-all.ps1

# 或双击
生产环境启动.bat
```
