"""
病程记录生成模块
"""
from typing import Optional
from datetime import datetime, timedelta
from database import DBManager
from ai_services import AIServiceManager
from knowledge_base import KnowledgeBaseManager


class ProgressNoteGenerator:
    """病程记录生成器"""

    def __init__(
        self,
        db_manager: DBManager,
        ai_manager: AIServiceManager,
        kb_manager: Optional[KnowledgeBaseManager] = None
    ):
        """初始化病程记录生成器

        Args:
            db_manager: 数据库管理器
            ai_manager: AI服务管理器
            kb_manager: 知识库管理器（可选）
        """
        self.db = db_manager
        self.ai = ai_manager
        self.kb = kb_manager

    def generate_note(
        self,
        hospital_number: str,
        daily_condition: str,
        record_type: str = "住院医师查房记录"
    ) -> dict:
        """生成病程记录

        Args:
            hospital_number: 住院号
            daily_condition: 当日情况
            record_type: 记录类型

        Returns:
            生成结果
        """
        # 获取患者信息
        patient = self.db.get_patient_by_hospital_number(hospital_number)
        if not patient:
            return {
                "success": False,
                "error": "患者不存在"
            }

        # 计算住院天数
        day_number = (datetime.now().date() - patient.admission_date).days + 1

        # 获取最近2次病程记录
        recent_notes = self.db.get_patient_notes(patient.id, limit=2)

        # 构建上下文
        context = {
            "name": patient.name or "未知",
            "gender": patient.gender or "未知",
            "age": patient.age or 0,
            "diagnosis": patient.diagnosis or "未诊断",
            "day_number": day_number,
            "initial_note": patient.initial_note or "",
            "daily_condition": daily_condition,
            "record_type": record_type,
            "recent_notes_1": recent_notes[0].generated_content if len(recent_notes) > 0 else "",
            "recent_notes_2": recent_notes[1].generated_content if len(recent_notes) > 1 else ""
        }

        # 如果有知识库，检索相关内容
        if self.kb:
            try:
                search_query = f"{patient.diagnosis} {daily_condition}"
                kb_results = self.kb.search(search_query, top_k=3)
                knowledge_content = "\n".join([
                    f"【来自 {r['source']}】\n{r['text']}\n"
                    for r in kb_results
                ])
                context["knowledge_base_content"] = knowledge_content
            except:
                context["knowledge_base_content"] = ""

        # 调用AI生成
        try:
            ai_service = self.ai.get_service()
            if not ai_service:
                return {
                    "success": False,
                    "error": "AI服务未配置"
                }

            generated_content = ai_service.generate_progress_note(context)

            # 保存到数据库
            note_data = {
                "patient_id": patient.id,
                "hospital_number": hospital_number,
                "record_date": datetime.now().date(),
                "day_number": day_number,
                "record_type": record_type,
                "daily_condition": daily_condition,
                "generated_content": generated_content,
                "is_edited": False
            }

            note_id = self.db.add_progress_note(note_data)

            return {
                "success": True,
                "note_id": note_id,
                "content": generated_content
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"AI生成失败: {str(e)}"
            }
