"""
患者管理API路由
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from sqlalchemy import or_

router = APIRouter()

# Pydantic模型
class PatientCreate(BaseModel):
    hospital_number: str
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    admission_date: date
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    past_history: Optional[str] = None
    allergy_history: Optional[str] = None
    specialist_exam: Optional[str] = None
    initial_note: Optional[str] = None

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    discharge_date: Optional[date] = None
    diagnosis: Optional[str] = None
    chief_complaint: Optional[str] = None
    past_history: Optional[str] = None
    allergy_history: Optional[str] = None
    specialist_exam: Optional[str] = None

class PatientResponse(BaseModel):
    id: int
    hospital_number: str
    name: Optional[str]
    gender: Optional[str]
    age: Optional[int]
    admission_date: date
    discharge_date: Optional[date]
    diagnosis: Optional[str]
    chief_complaint: Optional[str]
    # 计算字段：住院天数
    days_in_hospital: int

def get_session(request: Request):
    """获取数据库会话"""
    db_manager = request.app.state.db_manager
    return db_manager.get_session()

@router.get("/", response_model=List[PatientResponse])
async def get_patients(
    include_discharged: bool = False,
    search: Optional[str] = None,
    session = Depends(get_session)
):
    """获取患者列表"""
    try:
        from database.models import Patient

        query = session.query(Patient)

        # 过滤出院患者
        if not include_discharged:
            query = query.filter(Patient.discharge_date.is_(None))

        # 搜索功能
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Patient.name.like(search_pattern),
                    Patient.hospital_number.like(search_pattern),
                    Patient.diagnosis.like(search_pattern)
                )
            )

        patients = query.order_by(Patient.admission_date.desc()).all()

        # 计算住院天数并转换为响应模型
        result = []
        for p in patients:
            # 计算住院天数
            if p.discharge_date:
                days = (p.discharge_date - p.admission_date).days
            else:
                days = (datetime.now().date() - p.admission_date).days

            result.append(PatientResponse(
                id=p.id,
                hospital_number=p.hospital_number,
                name=p.name,
                gender=p.gender,
                age=p.age,
                admission_date=p.admission_date,
                discharge_date=p.discharge_date,
                diagnosis=p.diagnosis,
                chief_complaint=p.chief_complaint,
                days_in_hospital=days
            ))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{hospital_number}", response_model=PatientResponse)
async def get_patient(hospital_number: str, session = Depends(get_session)):
    """根据住院号获取患者"""
    try:
        from database.models import Patient

        patient = session.query(Patient).filter(
            Patient.hospital_number == hospital_number
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="患者不存在")

        # 计算住院天数
        if patient.discharge_date:
            days = (patient.discharge_date - patient.admission_date).days
        else:
            days = (datetime.now().date() - patient.admission_date).days

        return PatientResponse(
            id=patient.id,
            hospital_number=patient.hospital_number,
            name=patient.name,
            gender=patient.gender,
            age=patient.age,
            admission_date=patient.admission_date,
            discharge_date=patient.discharge_date,
            diagnosis=patient.diagnosis,
            chief_complaint=patient.chief_complaint,
            days_in_hospital=days
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=PatientResponse)
async def create_patient(patient: PatientCreate, session = Depends(get_session)):
    """创建新患者"""
    try:
        from database.models import Patient

        # 检查住院号是否已存在
        existing = session.query(Patient).filter(
            Patient.hospital_number == patient.hospital_number
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="住院号已存在")

        # 创建新患者
        new_patient = Patient(**patient.model_dump())
        session.add(new_patient)
        session.commit()
        session.refresh(new_patient)

        # 计算住院天数
        days = (datetime.now().date() - new_patient.admission_date).days

        return PatientResponse(
            id=new_patient.id,
            hospital_number=new_patient.hospital_number,
            name=new_patient.name,
            gender=new_patient.gender,
            age=new_patient.age,
            admission_date=new_patient.admission_date,
            discharge_date=new_patient.discharge_date,
            diagnosis=new_patient.diagnosis,
            chief_complaint=new_patient.chief_complaint,
            days_in_hospital=days
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{hospital_number}", response_model=PatientResponse)
async def update_patient(
    hospital_number: str,
    patient: PatientUpdate,
    session = Depends(get_session)
):
    """更新患者信息"""
    try:
        from database.models import Patient

        # 查找患者
        existing_patient = session.query(Patient).filter(
            Patient.hospital_number == hospital_number
        ).first()

        if not existing_patient:
            raise HTTPException(status_code=404, detail="患者不存在")

        # 更新字段
        update_data = patient.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing_patient, field, value)

        existing_patient.updated_at = datetime.now()
        session.commit()
        session.refresh(existing_patient)

        # 计算住院天数
        if existing_patient.discharge_date:
            days = (existing_patient.discharge_date - existing_patient.admission_date).days
        else:
            days = (datetime.now().date() - existing_patient.admission_date).days

        return PatientResponse(
            id=existing_patient.id,
            hospital_number=existing_patient.hospital_number,
            name=existing_patient.name,
            gender=existing_patient.gender,
            age=existing_patient.age,
            admission_date=existing_patient.admission_date,
            discharge_date=existing_patient.discharge_date,
            diagnosis=existing_patient.diagnosis,
            chief_complaint=existing_patient.chief_complaint,
            days_in_hospital=days
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{hospital_number}")
async def delete_patient(hospital_number: str, session = Depends(get_session)):
    """删除患者（软删除，设置出院日期）"""
    try:
        from database.models import Patient

        patient = session.query(Patient).filter(
            Patient.hospital_number == hospital_number
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="患者不存在")

        # 软删除：设置出院日期为今天
        patient.discharge_date = datetime.now().date()
        patient.updated_at = datetime.now()
        session.commit()

        return {"message": "患者已出院", "hospital_number": hospital_number}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
