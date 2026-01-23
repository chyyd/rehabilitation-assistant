"""
患者管理模块
"""
from typing import Optional
import json
from datetime import datetime
from database import DBManager
from ai_services import AIServiceManager


class PatientManager:
    """患者管理器"""

    def __init__(self, db_manager: DBManager, ai_manager: AIServiceManager):
        """初始化患者管理器

        Args:
            db_manager: 数据库管理器
            ai_manager: AI服务管理器
        """
        self.db = db_manager
        self.ai = ai_manager

    def create_patient(self, hospital_number: str, initial_note: str) -> dict:
        """创建新患者

        Args:
            hospital_number: 住院号
            initial_note: 首次病程记录

        Returns:
            创建结果
        """
        # 检查住院号是否已存在
        existing = self.db.get_patient_by_hospital_number(hospital_number)
        if existing:
            return {
                "success": False,
                "error": "该住院号已存在"
            }

        # 使用AI提取患者信息
        try:
            ai_service = self.ai.get_service()
            if not ai_service:
                return {
                    "success": False,
                    "error": "AI服务未配置"
                }

            extracted_info = ai_service.extract_patient_info(initial_note)

            # TODO: 解析AI返回的JSON

            # 构建患者数据
            patient_data = {
                "hospital_number": hospital_number,
                "name": "",  # 从extracted_info解析
                "gender": "",
                "age": 0,
                "admission_date": datetime.now().date(),
                "chief_complaint": "",
                "diagnosis": "",
                "past_history": "",
                "allergy_history": "",
                "specialist_exam": "",
                "initial_note": initial_note
            }

            # 保存到数据库
            patient_id = self.db.add_patient(patient_data)

            # 生成提醒
            self._generate_reminders(patient_id, patient_data)

            return {
                "success": True,
                "patient_id": patient_id,
                "extracted_info": extracted_info
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"患者信息提取失败: {str(e)}"
            }

    def _generate_reminders(self, patient_id: int, patient_data: dict):
        """为新患者生成提醒"""
        from datetime import timedelta, date

        admission_date = patient_data["admission_date"]

        # 第2天提醒：查看化验
        self.db.add_reminder({
            "patient_id": patient_id,
            "hospital_number": patient_data["hospital_number"],
            "reminder_type": "lab_review",
            "reminder_date": admission_date + timedelta(days=2),
            "day_number": 2,
            "description": "请查看化验检查结果",
            "priority": "中"
        })

        # 80天提醒
        self.db.add_reminder({
            "patient_id": patient_id,
            "hospital_number": patient_data["hospital_number"],
            "reminder_type": "duration_warning",
            "reminder_date": admission_date + timedelta(days=80),
            "day_number": 80,
            "description": "⚠️ 患者已住院80天，注意90天限制！",
            "priority": "高"
        })

        # 90天提醒
        self.db.add_reminder({
            "patient_id": patient_id,
            "hospital_number": patient_data["hospital_number"],
            "reminder_type": "duration_warning",
            "reminder_date": admission_date + timedelta(days=90),
            "day_number": 90,
            "description": "🚨 今日已达90天，必须准备出院或办理延长手续！",
            "priority": "紧急"
        })
