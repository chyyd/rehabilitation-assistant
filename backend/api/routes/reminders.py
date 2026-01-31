"""
提醒管理API路由
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

router = APIRouter()

# Pydantic模型
class ReminderResponse(BaseModel):
    id: int
    patient_id: int
    hospital_number: str
    reminder_type: str
    reminder_date: date
    day_number: Optional[int]
    description: str
    priority: str
    is_completed: bool
    completed_at: Optional[datetime]

def get_session(request: Request):
    """获取数据库会话"""
    db_manager = request.app.state.db_manager
    return db_manager.get_session()

@router.get("/today")
async def get_today_reminders(
    priority: Optional[str] = None,
    session = Depends(get_session)
):
    """获取今日提醒"""
    try:
        from database.models import Reminder, Patient
        from sqlalchemy import and_

        today = date.today()

        # 构建查询
        query = session.query(Reminder, Patient).join(
            Patient, Reminder.patient_id == Patient.id
        ).filter(
            and_(
                Reminder.reminder_date == today,
                Reminder.is_completed == False
            )
        )

        # 优先级过滤
        if priority:
            query = query.filter(Reminder.priority == priority)

        # 按优先级排序
        priority_order = {"紧急": 0, "高": 1, "中": 2, "低": 3}
        reminders = query.all()

        # 排序
        reminders.sort(key=lambda x: priority_order.get(x[0].priority, 4))

        # 格式化返回
        result = []
        for reminder, patient in reminders:
            result.append(ReminderResponse(
                id=reminder.id,
                patient_id=reminder.patient_id,
                hospital_number=reminder.hospital_number,
                reminder_type=reminder.reminder_type,
                reminder_date=reminder.reminder_date,
                day_number=reminder.day_number,
                description=reminder.description,
                priority=reminder.priority,
                is_completed=reminder.is_completed,
                completed_at=reminder.completed_at
            ))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{reminder_id}/complete")
async def mark_reminder_complete(
    reminder_id: int,
    session = Depends(get_session)
):
    """标记提醒完成"""
    try:
        from database.models import Reminder

        reminder = session.query(Reminder).filter(
            Reminder.id == reminder_id
        ).first()

        if not reminder:
            raise HTTPException(status_code=404, detail="提醒不存在")

        reminder.is_completed = True
        reminder.completed_at = datetime.now()

        session.commit()

        return {
            "success": True,
            "message": "提醒已标记为完成"
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient/{hospital_number}")
async def get_patient_reminders(
    hospital_number: str,
    upcoming: bool = False,
    session = Depends(get_session)
):
    """获取患者的提醒"""
    try:
        from database.models import Reminder, Patient

        # 获取患者
        patient = session.query(Patient).filter(
            Patient.hospital_number == hospital_number
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="患者不存在")

        # 获取提醒
        query = session.query(Reminder).filter(
            Reminder.patient_id == patient.id
        )

        if upcoming:
            # 只获取未完成的提醒
            query = query.filter(Reminder.is_completed == False)
            query = query.filter(Reminder.reminder_date >= date.today())

        reminders = query.order_by(Reminder.reminder_date.asc()).all()

        return [
            ReminderResponse(
                id=r.id,
                patient_id=r.patient_id,
                hospital_number=r.hospital_number,
                reminder_type=r.reminder_type,
                reminder_date=r.reminder_date,
                day_number=r.day_number,
                description=r.description,
                priority=r.priority,
                is_completed=r.is_completed,
                completed_at=r.completed_at
            )
            for r in reminders
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/patient/{hospital_number}/initialize")
async def initialize_patient_reminders(
    hospital_number: str,
    session = Depends(get_session)
):
    """为患者初始化提醒（创建初始待办事项）"""
    try:
        from database.models import Reminder, Patient

        # 获取患者
        patient = session.query(Patient).filter(
            Patient.hospital_number == hospital_number
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="患者不存在")

        # 检查是否已有提醒
        existing_count = session.query(Reminder).filter(
            Reminder.patient_id == patient.id
        ).count()

        if existing_count > 0:
            return {
                "success": True,
                "message": f"患者已有{existing_count}条提醒",
                "created_count": 0
            }

        # 计算住院天数
        days_in_hospital = (date.today() - patient.admission_date).days

        # 根据住院天数创建提醒
        reminders_to_create = []

        # 紧急提醒：住院超过85天
        if days_in_hospital >= 85:
            reminders_to_create.append({
                "reminder_type": "复查",
                "reminder_date": date.today(),
                "day_number": days_in_hospital + 1,
                "description": f"{patient.name or patient.hospital_number} 住院已超过85天，建议安排复查评估",
                "priority": "紧急"
            })

        # 高优先级：住院3天内
        if days_in_hospital <= 3:
            reminders_to_create.append({
                "reminder_type": "评估",
                "reminder_date": date.today(),
                "day_number": days_in_hospital + 1,
                "description": f"{patient.name or patient.hospital_number} 入院第{days_in_hospital + 1}天，完成初次康复评估",
                "priority": "高"
            })

        # 常规提醒：每日病程记录
        reminders_to_create.append({
            "reminder_type": "病程记录",
            "reminder_date": date.today(),
            "day_number": days_in_hospital + 1,
            "description": f"完成{patient.name or patient.hospital_number}的病程记录",
            "priority": "中"
        })

        # 批量创建提醒
        created_count = 0
        for reminder_data in reminders_to_create:
            new_reminder = Reminder(
                patient_id=patient.id,
                hospital_number=patient.hospital_number,
                **reminder_data
            )
            session.add(new_reminder)
            created_count += 1

        session.commit()

        return {
            "success": True,
            "message": f"成功创建{created_count}条提醒",
            "created_count": created_count
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
