"""
康复计划API路由
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
import json

router = APIRouter()

# Pydantic模型
class RehabPlanResponse(BaseModel):
    id: int
    patient_id: int
    hospital_number: str
    short_term_goals: Optional[str]
    long_term_goals: Optional[str]
    training_plan: Optional[str]
    created_at: date
    updated_at: date

class RehabProgressCreate(BaseModel):
    record_date: str
    content: str
    score: int

class RehabProgressResponse(BaseModel):
    id: int
    patient_id: int
    hospital_number: str
    record_date: date
    content: str
    score: int
    created_at: date

def get_session(request: Request):
    """获取数据库会话"""
    db_manager = request.app.state.db_manager
    return db_manager.get_session()

@router.get("/patient/{hospital_number}", response_model=RehabPlanResponse)
async def get_rehab_plan(hospital_number: str, session = Depends(get_session)):
    """获取患者康复计划"""
    try:
        from database.models import RehabPlan, Patient

        # 获取患者
        patient = session.query(Patient).filter(
            Patient.hospital_number == hospital_number
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="患者不存在")

        # 获取康复计划
        plan = session.query(RehabPlan).filter(
            RehabPlan.patient_id == patient.id
        ).first()

        if not plan:
            raise HTTPException(status_code=404, detail="康复计划不存在")

        return RehabPlanResponse(
            id=plan.id,
            patient_id=plan.patient_id,
            hospital_number=plan.hospital_number,
            short_term_goals=plan.short_term_goals,
            long_term_goals=plan.long_term_goals,
            training_plan=plan.training_plan,
            created_at=plan.created_at,
            updated_at=plan.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/patient/{hospital_number}", response_model=RehabPlanResponse)
async def create_rehab_plan(
    hospital_number: str,
    short_term_goals: str,
    long_term_goals: str,
    training_plan: str,
    session = Depends(get_session)
):
    """创建康复计划"""
    try:
        from database.models import RehabPlan, Patient

        # 获取患者
        patient = session.query(Patient).filter(
            Patient.hospital_number == hospital_number
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="患者不存在")

        # 检查是否已有康复计划
        existing = session.query(RehabPlan).filter(
            RehabPlan.patient_id == patient.id
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="患者已有康复计划")

        # 创建康复计划
        new_plan = RehabPlan(
            patient_id=patient.id,
            hospital_number=hospital_number,
            short_term_goals=short_term_goals,
            long_term_goals=long_term_goals,
            training_plan=training_plan
        )
        session.add(new_plan)
        session.commit()
        session.refresh(new_plan)

        return RehabPlanResponse(
            id=new_plan.id,
            patient_id=new_plan.patient_id,
            hospital_number=new_plan.hospital_number,
            short_term_goals=new_plan.short_term_goals,
            long_term_goals=new_plan.long_term_goals,
            training_plan=new_plan.training_plan,
            created_at=new_plan.created_at,
            updated_at=new_plan.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{hospital_number}/progress", response_model=List[RehabProgressResponse])
async def get_rehab_progress(hospital_number: str, session = Depends(get_session)):
    """获取康复进展记录"""
    try:
        from database.models import RehabProgress, Patient

        # 获取患者
        patient = session.query(Patient).filter(
            Patient.hospital_number == hospital_number
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="患者不存在")

        # 获取进展记录
        progress_list = session.query(RehabProgress).filter(
            RehabProgress.patient_id == patient.id
        ).order_by(RehabProgress.record_date.desc()).all()

        return [
            RehabProgressResponse(
                id=p.id,
                patient_id=p.patient_id,
                hospital_number=p.hospital_number,
                record_date=p.record_date,
                content=p.content,
                score=p.score,
                created_at=p.created_at
            )
            for p in progress_list
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{hospital_number}/progress")
async def create_rehab_progress(
    hospital_number: str,
    progress: RehabProgressCreate,
    session = Depends(get_session)
):
    """添加康复进展记录"""
    try:
        from database.models import RehabProgress, Patient

        # 获取患者
        patient = session.query(Patient).filter(
            Patient.hospital_number == hospital_number
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="患者不存在")

        # 创建进展记录
        new_progress = RehabProgress(
            patient_id=patient.id,
            hospital_number=hospital_number,
            record_date=datetime.fromisoformat(progress.record_date).date(),
            content=progress.content,
            score=progress.score
        )
        session.add(new_progress)
        session.commit()

        return {
            "success": True,
            "message": "进展记录已添加",
            "id": new_progress.id
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
