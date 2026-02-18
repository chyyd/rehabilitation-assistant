"""
AI服务API路由
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

router = APIRouter()

# Pydantic模型
class ExtractInfoRequest(BaseModel):
    initial_note: str

class GenerateNoteRequest(BaseModel):
    hospital_number: str
    daily_condition: str
    record_type: str = "住院医师查房"
    use_knowledge_base: bool = True
    doctor_info: Optional[dict] = None  # 医生信息（姓名、职称等）

class GenerateRehabPlanRequest(BaseModel):
    hospital_number: str

class TestAIServiceRequest(BaseModel):
    service: str
    api_key: str
    base_url: str
    model: str

class TestEmbeddingRequest(BaseModel):
    service: str
    api_key: str
    base_url: str
    model: str

def get_session(request: Request):
    """获取数据库会话"""
    db_manager = request.app.state.db_manager
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()

def get_managers(request: Request):
    """获取管理器依赖"""
    return {
        'ai_manager': request.app.state.ai_manager,
        'kb_manager': request.app.state.kb_manager
    }

@router.post("/extract-patient-info")
async def extract_patient_info(
    request: ExtractInfoRequest,
    managers = Depends(get_managers)
):
    """从首次病程记录提取患者信息"""
    try:
        ai_manager = managers['ai_manager']

        # 获取AI服务
        ai_service = ai_manager.get_service()
        if not ai_service:
            raise HTTPException(status_code=400, detail="AI服务未配置")

        # 调用AI提取信息
        extracted_info = ai_service.extract_patient_info(request.initial_note)

        # 打印提取结果用于调试
        print(f"[DEBUG] AI提取的患者信息: {extracted_info}")

        return {
            "success": True,
            "data": extracted_info
        }
    except HTTPException:
        raise
    except Exception as e:
        # 打印详细错误信息
        print(f"[ERROR] 提取患者信息失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"提取失败: {str(e)}")

@router.post("/generate-note")
async def generate_note(
    request: GenerateNoteRequest,
    session = Depends(get_session),
    managers = Depends(get_managers)
):
    """AI生成病程记录"""
    try:
        ai_manager = managers['ai_manager']
        kb_manager = managers['kb_manager']

        # 获取患者信息
        from database.models import Patient
        patient = session.query(Patient).filter(
            Patient.hospital_number == request.hospital_number
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="患者不存在")

        # 获取AI服务
        ai_service = ai_manager.get_service()
        if not ai_service:
            raise HTTPException(status_code=400, detail="AI服务未配置")

        # 计算住院天数（入院当天算第1天，所以需要 +1）
        # 重要：使用用户选择的记录日期，而不是当前日期（修复补记录时日期错误问题）
        from datetime import date
        admission_date = patient.admission_date if isinstance(patient.admission_date, date) else patient.admission_date.date()
        record_date = request.record_date if isinstance(request.record_date, date) else request.record_date.date()
        days_in_hospital = (record_date - admission_date).days + 1

        # 获取历史记录（最近2次）
        from database.models import ProgressNote
        recent_notes = session.query(ProgressNote).filter(
            ProgressNote.patient_id == patient.id
        ).order_by(ProgressNote.record_date.desc()).limit(2).all()

        # 构建上下文（扁平化结构，符合AI服务期望）
        context = {
            "name": patient.name,
            "gender": patient.gender,
            "age": patient.age,
            "diagnosis": patient.diagnosis,
            "day_number": days_in_hospital,
            "daily_condition": request.daily_condition,
            "record_type": request.record_type,
            "initial_note": patient.initial_note,
            "doctor_info": request.doctor_info  # 添加医生信息
        }

        # 添加最近病程记录
        if len(recent_notes) >= 1:
            context["recent_notes_1"] = f"{recent_notes[0].record_type} {recent_notes[0].generated_content[:100] if recent_notes[0].generated_content else ''}"
        if len(recent_notes) >= 2:
            context["recent_notes_2"] = f"{recent_notes[1].record_type} {recent_notes[1].generated_content[:100] if recent_notes[1].generated_content else ''}"

        # 如果启用知识库且有知识库管理器
        if request.use_knowledge_base and kb_manager:
            try:
                # 从知识库搜索相关内容
                search_query = f"{patient.diagnosis} {request.daily_condition}"
                kb_results = kb_manager.search(search_query, top_k=3)
                context["knowledge_base"] = kb_results
            except Exception as e:
                print(f"知识库搜索失败: {e}")
                context["knowledge_base"] = []

        # 调用AI生成病程记录
        generated_content = ai_service.generate_progress_note(context)

        return {
            "success": True,
            "data": {
                "content": generated_content,
                "record_type": request.record_type
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")

@router.post("/generate-rehab-plan")
async def generate_rehab_plan(
    request: GenerateRehabPlanRequest,
    session = Depends(get_session),
    managers = Depends(get_managers)
):
    """生成康复计划"""
    try:
        ai_manager = managers['ai_manager']
        kb_manager = managers['kb_manager']

        # 获取患者信息
        from database.models import Patient, RehabPlan
        patient = session.query(Patient).filter(
            Patient.hospital_number == request.hospital_number
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="患者不存在")

        # 获取AI服务
        ai_service = ai_manager.get_service()
        if not ai_service:
            raise HTTPException(status_code=400, detail="AI服务未配置")

        # 构建上下文
        context = {
            "patient_info": {
                "name": patient.name,
                "gender": patient.gender,
                "age": patient.age,
                "diagnosis": patient.diagnosis,
                "chief_complaint": patient.chief_complaint,
                "specialist_exam": patient.specialist_exam
            },
            "initial_note": patient.initial_note
        }

        # 如果有知识库，搜索相关康复方案
        if kb_manager:
            try:
                search_query = f"{patient.diagnosis} 康复训练 方案"
                kb_results = kb_manager.search(search_query, top_k=5)
                context["knowledge_base"] = [
                    {"text": r["text"], "source": r["source"]}
                    for r in kb_results
                ]
            except Exception as e:
                print(f"知识库搜索失败: {e}")
                context["knowledge_base"] = []

        # 调用AI生成康复计划
        rehab_plan_data = ai_service.generate_rehab_plan(context)

        # 检查患者是否已有康复计划
        existing_plan = session.query(RehabPlan).filter(
            RehabPlan.patient_id == patient.id
        ).first()

        if existing_plan:
            # 更新现有计划
            existing_plan.short_term_goals = rehab_plan_data.get('short_term_goals')
            existing_plan.long_term_goals = rehab_plan_data.get('long_term_goals')
            existing_plan.training_plan = rehab_plan_data.get('training_plan')
        else:
            # 创建新康复计划
            new_plan = RehabPlan(
                patient_id=patient.id,
                hospital_number=request.hospital_number,
                short_term_goals=rehab_plan_data.get('short_term_goals'),
                long_term_goals=rehab_plan_data.get('long_term_goals'),
                training_plan=rehab_plan_data.get('training_plan')
            )
            session.add(new_plan)

        session.commit()

        return {
            "success": True,
            "data": rehab_plan_data
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")

@router.post("/test")
async def test_ai_service(request: TestAIServiceRequest):
    """测试AI服务连接"""
    try:
        from ai_services.service_manager import AIServiceManager
        from openai import OpenAI

        # 创建临时客户端测试连接
        client = OpenAI(
            api_key=request.api_key,
            base_url=request.base_url
        )

        # 发送测试请求
        response = client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "user", "content": "测试连接"}
            ],
            max_tokens=10,
            temperature=0.5
        )

        return {
            "success": True,
            "message": "连接测试成功",
            "model": request.model
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"连接失败: {str(e)}")

@router.post("/test-embedding")
async def test_embedding_service(request: TestEmbeddingRequest):
    """测试Embedding服务连接"""
    try:
        from openai import OpenAI

        # 创建临时客户端测试连接
        client = OpenAI(
            api_key=request.api_key,
            base_url=request.base_url
        )

        # 发送测试请求
        response = client.embeddings.create(
            model=request.model,
            input="测试文本"
        )

        return {
            "success": True,
            "message": "Embedding连接测试成功",
            "model": request.model,
            "dimension": len(response.data[0].embedding)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"连接失败: {str(e)}")

class UpdateAIConfigRequest(BaseModel):
    """更新AI配置请求"""
    default_service: str
    services: dict

@router.post("/update-config")
async def update_ai_config(
    request: UpdateAIConfigRequest,
    app_request: Request
):
    """更新AI服务配置"""
    try:
        import json
        import os
        from ai_services.service_manager import AIServiceManager

        ai_manager = app_request.app.state.ai_manager

        # 重新初始化AI服务管理器
        new_manager = AIServiceManager({"ai_services": request.services})

        # 更新app中的ai_manager
        app_request.app.state.ai_manager = new_manager

        # 将配置写入config.json文件
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "config.json")

        try:
            # 读取现有配置
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 更新ai_services部分
            if "ai_services" not in config:
                config["ai_services"] = {}

            config["ai_services"]["default_service"] = request.default_service

            # 更新各个服务的配置
            for provider, settings in request.services.items():
                if provider not in config["ai_services"]:
                    config["ai_services"][provider] = {}

                config["ai_services"][provider].update(settings)

            # 写回文件
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"写入config.json失败: {e}")
            # 不阻断配置更新流程

        return {
            "success": True,
            "message": "AI配置已更新并已保存"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")
