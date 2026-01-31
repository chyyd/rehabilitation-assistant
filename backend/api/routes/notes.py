"""
病程记录API路由
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime

router = APIRouter()

# Pydantic模型
class NoteCreate(BaseModel):
    hospital_number: str
    record_date: date
    record_type: str
    daily_condition: str
    generated_content: str

class NoteUpdate(BaseModel):
    daily_condition: Optional[str] = None
    generated_content: Optional[str] = None
    is_edited: Optional[bool] = None

class NoteResponse(BaseModel):
    id: int
    hospital_number: str
    record_date: date
    day_number: int
    record_type: str
    daily_condition: str
    generated_content: str
    is_edited: bool
    created_at: datetime

def get_session(request: Request):
    """获取数据库会话"""
    db_manager = request.app.state.db_manager
    return db_manager.get_session()

@router.get("/patient/{hospital_number}", response_model=List[NoteResponse])
async def get_patient_notes(
    hospital_number: str,
    limit: int = 10,
    session = Depends(get_session)
):
    """获取患者的病程记录"""
    try:
        from database.models import ProgressNote, Patient

        # 先获取患者
        patient = session.query(Patient).filter(
            Patient.hospital_number == hospital_number
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="患者不存在")

        # 获取病程记录
        notes = session.query(ProgressNote).filter(
            ProgressNote.patient_id == patient.id
        ).order_by(ProgressNote.record_date.desc()).limit(limit).all()

        return [
            NoteResponse(
                id=note.id,
                hospital_number=note.hospital_number,
                record_date=note.record_date,
                day_number=note.day_number,
                record_type=note.record_type,
                daily_condition=note.daily_condition,
                generated_content=note.generated_content,
                is_edited=note.is_edited,
                created_at=note.created_at
            )
            for note in notes
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=NoteResponse)
async def create_note(note: NoteCreate, session = Depends(get_session)):
    """创建病程记录"""
    try:
        from database.models import ProgressNote, Patient

        # 获取患者
        patient = session.query(Patient).filter(
            Patient.hospital_number == note.hospital_number
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="患者不存在")

        # 计算住院天数
        day_number = (note.record_date - patient.admission_date).days + 1

        # 创建病程记录
        new_note = ProgressNote(
            patient_id=patient.id,
            hospital_number=note.hospital_number,
            record_date=note.record_date,
            day_number=day_number,
            record_type=note.record_type,
            daily_condition=note.daily_condition,
            generated_content=note.generated_content,
            is_edited=False
        )

        session.add(new_note)
        session.commit()
        session.refresh(new_note)

        return NoteResponse(
            id=new_note.id,
            hospital_number=new_note.hospital_number,
            record_date=new_note.record_date,
            day_number=new_note.day_number,
            record_type=new_note.record_type,
            daily_condition=new_note.daily_condition,
            generated_content=new_note.generated_content,
            is_edited=new_note.is_edited,
            created_at=new_note.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note: NoteUpdate,
    session = Depends(get_session)
):
    """更新病程记录"""
    try:
        from database.models import ProgressNote

        existing_note = session.query(ProgressNote).filter(
            ProgressNote.id == note_id
        ).first()

        if not existing_note:
            raise HTTPException(status_code=404, detail="病程记录不存在")

        # 更新字段
        update_data = note.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing_note, field, value)

        # 如果修改了内容，标记为已编辑
        if 'generated_content' in update_data:
            existing_note.is_edited = True

        session.commit()
        session.refresh(existing_note)

        return NoteResponse(
            id=existing_note.id,
            hospital_number=existing_note.hospital_number,
            record_date=existing_note.record_date,
            day_number=existing_note.day_number,
            record_type=existing_note.record_type,
            daily_condition=existing_note.daily_condition,
            generated_content=existing_note.generated_content,
            is_edited=existing_note.is_edited,
            created_at=existing_note.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, session = Depends(get_session)):
    """获取单个病程记录"""
    try:
        from database.models import ProgressNote

        note = session.query(ProgressNote).filter(
            ProgressNote.id == note_id
        ).first()

        if not note:
            raise HTTPException(status_code=404, detail="病程记录不存在")

        return NoteResponse(
            id=note.id,
            hospital_number=note.hospital_number,
            record_date=note.record_date,
            day_number=note.day_number,
            record_type=note.record_type,
            daily_condition=note.daily_condition,
            generated_content=note.generated_content,
            is_edited=note.is_edited,
            created_at=note.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
