"""
数据库管理器
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from pathlib import Path
from typing import Optional
import json

from database.models import Base, Patient, ProgressNote, Reminder, Template, Doctor


class DBManager:
    """数据库管理器"""

    def __init__(self, db_path: str = "./rehab_assistant.db"):
        """初始化数据库连接"""
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.create_tables()

    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()

    # 患者相关操作
    def add_patient(self, patient_data: dict) -> int:
        """添加患者，返回患者ID"""
        with self.get_session() as session:
            patient = Patient(**patient_data)
            session.add(patient)
            session.commit()
            session.refresh(patient)
            return patient.id

    def get_patient_by_hospital_number(self, hospital_number: str) -> Optional[Patient]:
        """根据住院号获取患者"""
        with self.get_session() as session:
            return session.query(Patient).filter(
                Patient.hospital_number == hospital_number
            ).first()

    def get_all_patients(self, include_discharged: bool = False) -> list[Patient]:
        """获取所有患者"""
        with self.get_session() as session:
            query = session.query(Patient)
            if not include_discharged:
                query = query.filter(Patient.discharge_date.is_(None))
            return query.all()

    def update_patient(self, hospital_number: str, update_data: dict) -> bool:
        """更新患者信息"""
        with self.get_session() as session:
            patient = session.query(Patient).filter(
                Patient.hospital_number == hospital_number
            ).first()
            if patient:
                for key, value in update_data.items():
                    setattr(patient, key, value)
                session.commit()
                return True
            return False

    # 病程记录相关操作
    def add_progress_note(self, note_data: dict) -> int:
        """添加病程记录"""
        with self.get_session() as session:
            note = ProgressNote(**note_data)
            session.add(note)
            session.commit()
            session.refresh(note)
            return note.id

    def get_patient_notes(self, patient_id: int, limit: int = 5) -> list[ProgressNote]:
        """获取患者的最近病程记录"""
        with self.get_session() as session:
            return session.query(ProgressNote).filter(
                ProgressNote.patient_id == patient_id
            ).order_by(ProgressNote.record_date.desc()).limit(limit).all()

    # 提醒相关操作
    def add_reminder(self, reminder_data: dict) -> int:
        """添加提醒"""
        with self.get_session() as session:
            reminder = Reminder(**reminder_data)
            session.add(reminder)
            session.commit()
            session.refresh(reminder)
            return reminder.id

    def get_today_reminders(self, priority_filter: str = None) -> list[Reminder]:
        """获取今日待完成提醒"""
        from datetime import date
        with self.get_session() as session:
            query = session.query(Reminder).filter(
                Reminder.reminder_date == date.today(),
                Reminder.is_completed == False
            )
            if priority_filter:
                query = query.filter(Reminder.priority == priority_filter)
            return query.order_by(Reminder.priority.desc()).all()

    def mark_reminder_completed(self, reminder_id: int) -> bool:
        """标记提醒为已完成"""
        from datetime import date
        with self.get_session() as session:
            reminder = session.query(Reminder).filter(Reminder.id == reminder_id).first()
            if reminder:
                reminder.is_completed = True
                reminder.completed_at = date.today()
                session.commit()
                return True
            return False

    # 模板相关操作
    def add_template(self, template_data: dict) -> int:
        """添加模板"""
        with self.get_session() as session:
            template = Template(**template_data)
            session.add(template)
            session.commit()
            session.refresh(template)
            return template.id

    def get_templates_by_category(self, category: str) -> list[Template]:
        """按分类获取模板"""
        with self.get_session() as session:
            return session.query(Template).filter(
                Template.category == category
            ).order_by(Template.usage_count.desc()).all()

    def increment_template_usage(self, template_id: int):
        """增加模板使用次数"""
        with self.get_session() as session:
            template = session.query(Template).filter(Template.id == template_id).first()
            if template:
                template.usage_count += 1
                session.commit()
