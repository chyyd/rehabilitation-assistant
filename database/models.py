"""
SQLAlchemy数据模型定义
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base

Base = declarative_base()

class Patient(Base):
    """患者信息表"""
    __tablename__ = 'patients'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hospital_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(50))
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    age: Mapped[Optional[int]] = mapped_column(Integer)
    admission_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    discharge_date: Mapped[Optional[datetime]] = mapped_column(Date)
    chief_complaint: Mapped[Optional[str]] = mapped_column(Text)
    diagnosis: Mapped[Optional[str]] = mapped_column(Text)
    past_history: Mapped[Optional[str]] = mapped_column(Text)
    allergy_history: Mapped[Optional[str]] = mapped_column(Text)
    specialist_exam: Mapped[Optional[str]] = mapped_column(Text)
    initial_note: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(Date, default=datetime.now, onupdate=datetime.now)

    # 关系
    progress_notes: Mapped[list["ProgressNote"]] = relationship("ProgressNote", back_populates="patient", cascade="all, delete-orphan")
    reminders: Mapped[list["Reminder"]] = relationship("Reminder", back_populates="patient", cascade="all, delete-orphan")
    rehab_plan: Mapped[Optional["RehabPlan"]] = relationship("RehabPlan", back_populates="patient", uselist=False, cascade="all, delete-orphan")
    rehab_progress: Mapped[list["RehabProgress"]] = relationship("RehabProgress", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient(hospital_number={self.hospital_number}, name={self.name})>"


class ProgressNote(Base):
    """病程记录表"""
    __tablename__ = 'progress_notes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey('patients.id'), nullable=False)
    hospital_number: Mapped[str] = mapped_column(String(50), nullable=False)
    record_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    record_type: Mapped[str] = mapped_column(String(50), nullable=False)
    daily_condition: Mapped[Optional[str]] = mapped_column(Text)
    generated_content: Mapped[Optional[str]] = mapped_column(Text)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.now)

    # 关系
    patient: Mapped["Patient"] = relationship("Patient", back_populates="progress_notes")

    def __repr__(self):
        return f"<ProgressNote(date={self.record_date}, type={self.record_type})>"


class Reminder(Base):
    """提醒表"""
    __tablename__ = 'reminders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey('patients.id'), nullable=False)
    hospital_number: Mapped[str] = mapped_column(String(50), nullable=False)
    reminder_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reminder_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    day_number: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)  # 紧急/高/中/低
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.now)

    # 关系
    patient: Mapped["Patient"] = relationship("Patient", back_populates="reminders")

    def __repr__(self):
        return f"<Reminder(type={self.reminder_type}, date={self.reminder_date})>"


class Template(Base):
    """模板表"""
    __tablename__ = 'templates'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    template_name: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.now)

    def __repr__(self):
        return f"<Template(name={self.template_name}, category={self.category})>"


class Doctor(Base):
    """医师表"""
    __tablename__ = 'doctors'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    roles: Mapped[str] = mapped_column(String(200), nullable=False)  # 逗号分隔
    default_roles: Mapped[str] = mapped_column(String(200), nullable=False)  # 逗号分隔
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.now)

    def __repr__(self):
        return f"<Doctor(name={self.doctor_name}, roles={self.roles})>"


class RehabPlan(Base):
    """康复计划表"""
    __tablename__ = 'rehab_plans'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey('patients.id'), nullable=False)
    hospital_number: Mapped[str] = mapped_column(String(50), nullable=False)
    short_term_goals: Mapped[Optional[str]] = mapped_column(Text)  # 短期目标（1-2周）
    long_term_goals: Mapped[Optional[str]] = mapped_column(Text)  # 长期目标（1-3个月）
    training_plan: Mapped[Optional[str]] = mapped_column(Text)  # JSON格式的训练计划
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(Date, default=datetime.now, onupdate=datetime.now)

    # 关系
    patient: Mapped["Patient"] = relationship("Patient", back_populates="rehab_plan")

    def __repr__(self):
        return f"<RehabPlan(hospital_number={self.hospital_number})>"


class RehabProgress(Base):
    """康复进展记录表"""
    __tablename__ = 'rehab_progress'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey('patients.id'), nullable=False)
    hospital_number: Mapped[str] = mapped_column(String(50), nullable=False)
    record_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=3)  # 1-5星评分
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.now)

    # 关系
    patient: Mapped["Patient"] = relationship("Patient", back_populates="rehab_progress")

    def __repr__(self):
        return f"<RehabProgress(date={self.record_date}, score={self.score})>"
