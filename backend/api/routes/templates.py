"""
模板管理API路由
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Pydantic模型
class TemplateCreate(BaseModel):
    category: str
    template_name: str
    content: str
    is_system: bool = False

class TemplateUpdate(BaseModel):
    template_name: Optional[str] = None
    content: Optional[str] = None

class TemplateResponse(BaseModel):
    id: int
    category: str
    template_name: str
    content: str
    is_system: bool
    usage_count: int

def get_session(request: Request):
    """获取数据库会话"""
    db_manager = request.app.state.db_manager
    return db_manager.get_session()

@router.get("/")
async def get_templates(
    category: Optional[str] = None,
    session = Depends(get_session)
):
    """获取模板列表"""
    try:
        from database.models import Template

        query = session.query(Template)

        if category:
            query = query.filter(Template.category == category)

        templates = query.order_by(Template.usage_count.desc()).all()

        return [
            TemplateResponse(
                id=t.id,
                category=t.category,
                template_name=t.template_name,
                content=t.content,
                is_system=t.is_system,
                usage_count=t.usage_count
            )
            for t in templates
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=TemplateResponse)
async def create_template(
    template: TemplateCreate,
    session = Depends(get_session)
):
    """创建模板"""
    try:
        from database.models import Template

        new_template = Template(**template.model_dump())
        session.add(new_template)
        session.commit()
        session.refresh(new_template)

        return TemplateResponse(
            id=new_template.id,
            category=new_template.category,
            template_name=new_template.template_name,
            content=new_template.content,
            is_system=new_template.is_system,
            usage_count=new_template.usage_count
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template: TemplateUpdate,
    session = Depends(get_session)
):
    """更新模板"""
    try:
        from database.models import Template

        existing_template = session.query(Template).filter(
            Template.id == template_id
        ).first()

        if not existing_template:
            raise HTTPException(status_code=404, detail="模板不存在")

        # 系统模板不允许修改
        if existing_template.is_system:
            raise HTTPException(status_code=400, detail="系统模板不允许修改")

        # 更新字段
        update_data = template.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing_template, field, value)

        session.commit()
        session.refresh(existing_template)

        return TemplateResponse(
            id=existing_template.id,
            category=existing_template.category,
            template_name=existing_template.template_name,
            content=existing_template.content,
            is_system=existing_template.is_system,
            usage_count=existing_template.usage_count
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{template_id}")
async def delete_template(template_id: int, session = Depends(get_session)):
    """删除模板"""
    try:
        from database.models import Template

        template = session.query(Template).filter(
            Template.id == template_id
        ).first()

        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")

        # 系统模板不允许删除
        if template.is_system:
            raise HTTPException(status_code=400, detail="系统模板不允许删除")

        session.delete(template)
        session.commit()

        return {"success": True, "message": "模板已删除"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{template_id}/use")
async def use_template(template_id: int, session = Depends(get_session)):
    """使用模板（增加使用计数）"""
    try:
        from database.models import Template

        template = session.query(Template).filter(
            Template.id == template_id
        ).first()

        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")

        template.usage_count += 1
        session.commit()

        return {"success": True, "usage_count": template.usage_count}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 新增Pydantic模型
class ExtractPhrasesRequest(BaseModel):
    content: str
    filename: Optional[str] = None

class PhraseItem(BaseModel):
    content: str
    category: str

class BatchCreateRequest(BaseModel):
    phrases: List[PhraseItem]

def get_managers(request: Request):
    """获取管理器依赖"""
    return {
        'ai_manager': request.app.state.ai_manager
    }

@router.post("/extract-phrases")
async def extract_phrases(
    request: ExtractPhrasesRequest,
    managers = Depends(get_managers)
):
    """AI提取常用语句并分类"""
    try:
        ai_manager = managers['ai_manager']

        # 获取AI服务
        ai_service = ai_manager.get_default_service()
        if not ai_service:
            raise HTTPException(status_code=400, detail="AI服务未配置")

        # 第一步：Python预处理 - 提取高频语句
        from utils.text_processor import preprocess_medical_records, optimize_phrases_for_ai

        preprocessed_phrases = preprocess_medical_records(request.content, max_phrases=80)

        if not preprocessed_phrases:
            return {
                "success": True,
                "phrases": [],
                "message": "未能从文档中提取到有效语句"
            }

        # 第二步：将预处理后的语句格式化
        phrases_text = optimize_phrases_for_ai(preprocessed_phrases, max_content_length=8000)

        # 第三步：调用AI优化和分类
        extracted_phrases = ai_service.extract_common_phrases(phrases_text, preprocessed=True)

        return {
            "success": True,
            "phrases": extracted_phrases,
            "preprocessed_count": len(preprocessed_phrases),
            "message": f"从文档中预处理提取了 {len(preprocessed_phrases)} 条语句，AI优化分类后返回 {len(extracted_phrases)} 条"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"提取失败: {str(e)}")

@router.post("/batch")
async def batch_create_templates(
    request: BatchCreateRequest,
    session = Depends(get_session)
):
    """批量创建模板"""
    try:
        from database.models import Template

        created_count = 0
        for phrase in request.phrases:
            # 生成模板名称（取内容前20个字符）
            template_name = phrase.content[:20] + "..." if len(phrase.content) > 20 else phrase.content

            new_template = Template(
                category=phrase.category,
                template_name=template_name,
                content=phrase.content,
                is_system=False,
                usage_count=0
            )
            session.add(new_template)
            created_count += 1

        session.commit()

        return {
            "success": True,
            "created_count": created_count,
            "message": f"成功创建 {created_count} 条模板"
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
