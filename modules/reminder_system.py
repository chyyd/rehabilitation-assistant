"""
提醒系统模块
"""
from datetime import date, datetime, timedelta
from database import DBManager
from utils.date_calculator import DateCalculator


class ReminderSystem:
    """提醒系统"""

    def __init__(self, db_manager: DBManager):
        """初始化提醒系统

        Args:
            db_manager: 数据库管理器
        """
        self.db = db_manager
        self.date_calculator = DateCalculator()

    def get_today_reminders(self) -> list[dict]:
        """获取今日所有待完成提醒，按优先级排序"""
        reminders = self.db.get_today_reminders()

        # 格式化返回
        formatted = []
        for r in reminders:
            formatted.append({
                "id": r.id,
                "hospital_number": r.hospital_number,
                "type": r.reminder_type,
                "description": r.description,
                "priority": r.priority,
                "day_number": r.day_number
            })

        return formatted

    def mark_completed(self, reminder_id: int) -> bool:
        """标记提醒为已完成"""
        return self.db.mark_reminder_completed(reminder_id)

    def generate_rounds_reminders(self, patient_id: int, admission_date: date, discharge_date: date):
        """生成查房记录提醒（基于rounds_generator逻辑）"""
        records = self.date_calculator.generate_all_reminders(
            admission_date.strftime("%Y-%m-%d"),
            discharge_date.strftime("%Y-%m-%d")
        )

        for record in records:
            # 确定优先级
            if "主治医师" in record["type"]:
                priority = "中"
            elif "主任医师" in record["type"]:
                priority = "中"
            elif "阶段小结" in record["type"]:
                priority = "高"
            else:
                priority = "中"

            self.db.add_reminder({
                "patient_id": patient_id,
                "hospital_number": "",  # TODO: 从patient获取
                "reminder_type": "progress_note",
                "reminder_date": datetime.strptime(record["date"], "%Y-%m-%d").date(),
                "day_number": record["day"],
                "description": f"需书写{record['type']}记录",
                "priority": priority
            })
