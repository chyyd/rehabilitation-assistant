"""
FastAPI后端服务
为Electron前端提供API接口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

# 导入现有模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DBManager
from ai_services import AIServiceManager
from knowledge_base import KnowledgeBaseManager

# 全局管理器实例
db_manager = None
ai_manager = None
kb_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global db_manager, ai_manager, kb_manager

    # 启动时初始化
    print("启动FastAPI后端服务...")

    import json
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 初始化数据库
    db_manager = DBManager(config["app"]["database_path"])
    print("[OK] 数据库初始化完成")

    # 初始化AI服务
    ai_manager = AIServiceManager(config)
    print("[OK] AI服务初始化完成")

    # 初始化知识库
    if ai_manager.get_embedder():
        kb_manager = KnowledgeBaseManager(
            config["knowledge_base"],
            ai_manager.get_embedder()
        )
        print("[OK] 知识库初始化完成")
    else:
        print("[WARN] 知识库未初始化（未配置Embedding服务）")
        kb_manager = None

    # 将管理器存储在app state中以便路由访问
    app.state.db_manager = db_manager
    app.state.ai_manager = ai_manager
    app.state.kb_manager = kb_manager

    yield

    # 关闭时清理
    print("关闭FastAPI后端服务...")

# 创建FastAPI应用
app = FastAPI(
    title="康复科助手API",
    description="为Electron桌面应用提供后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS（允许Electron本地访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由
from backend.api.routes import patients, notes, reminders, templates, ai, rehab_plans, knowledge

# 注册路由
app.include_router(patients.router, prefix="/api/patients", tags=["患者管理"])
app.include_router(notes.router, prefix="/api/notes", tags=["病程记录"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["提醒管理"])
app.include_router(templates.router, prefix="/api/templates", tags=["模板管理"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI服务"])
app.include_router(rehab_plans.router, prefix="/api/rehab-plan", tags=["康复计划"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["知识库"])

@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "康复科助手API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "api_main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
