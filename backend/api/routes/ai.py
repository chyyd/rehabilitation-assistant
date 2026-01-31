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

def get_session(request: Request):
    """获取数据库会话"""
    db_manager = request.app.state.db_manager
    return db_manager.get_session()

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
        ai_service = ai_manager.get_default_service()
        if not ai_service:
            raise HTTPException(status_code=400, detail="AI服务未配置")

        # 调用AI提取信息
        extracted_info = ai_service.extract_patient_info(request.initial_note)

        return {
            "success": True,
            "data": extracted_info
        }
    except HTTPException:
        raise
    except Exception as e:
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
        ai_service = ai_manager.get_default_service()
        if not ai_service:
            raise HTTPException(status_code=400, detail="AI服务未配置")

        # 计算住院天数
        from datetime import date
        admission_date = patient.admission_date if isinstance(patient.admission_date, date) else patient.admission_date.date()
        days_in_hospital = (date.today() - admission_date).days

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
        ai_service = ai_manager.get_default_service()
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
