"""
知识库管理API路由
"""
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

router = APIRouter()

# Pydantic模型
class KnowledgeFileResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    upload_date: str
    file_path: str

def get_session(request: Request):
    """获取数据库会话"""
    db_manager = request.app.state.db_manager
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()

@router.get("/files", response_model=List[KnowledgeFileResponse])
async def get_knowledge_files(session = Depends(get_session)):
    """获取知识库文件列表"""
    try:
        # 暂时返回空列表，等待知识库表创建
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_knowledge_file(
    file: UploadFile = File(...),
    session = Depends(get_session)
):
    """上传知识库文件"""
    try:
        # 检查文件类型
        allowed_extensions = {'.txt', '.pdf', '.doc', '.docx', '.md'}
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型。允许的类型：{', '.join(allowed_extensions)}"
            )

        # TODO: 实现文件保存和知识库索引
        # 1. 保存文件到知识库目录
        # 2. 调用kb_manager索引文件
        # 3. 在数据库中记录文件信息

        return {
            "success": True,
            "message": "文件上传成功（功能待完善）",
            "filename": file.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/{file_id}")
async def delete_knowledge_file(file_id: int, session = Depends(get_session)):
    """删除知识库文件"""
    try:
        # TODO: 实现文件删除
        # 1. 从数据库获取文件信息
        # 2. 删除物理文件
        # 3. 从知识库索引中移除
        # 4. 从数据库删除记录

        return {
            "success": True,
            "message": "文件删除成功（功能待完善）"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
