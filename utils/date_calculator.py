"""
日期计算器 - 生成查房记录提醒
"""
from datetime import datetime, timedelta
from typing import List, Dict


class DateCalculator:
    """日期计算器"""

    def generate_all_reminders(self, admission_date: str, discharge_date: str) -> List[Dict]:
        """生成所有查房记录提醒

        Args:
            admission_date: 入院日期 (YYYY-MM-DD)
            discharge_date: 出院日期 (YYYY-MM-DD)

        Returns:
            提醒记录列表
        """
        start = datetime.strptime(admission_date, "%Y-%m-%d")
        end = datetime.strptime(discharge_date, "%Y-%m-%d")

        records = []
        current = start
        day = 1

        while current <= end:
            # 第1天：首次病程记录
            if day == 1:
                records.append({
                    "date": current.strftime("%Y-%m-%d"),
                    "day": day,
                    "type": "首次病程记录"
                })

            # 每天住院医师查房记录
            records.append({
                "date": current.strftime("%Y-%m-%d"),
                "day": day,
                "type": "住院医师查房记录"
            })

            # 主治医师查房记录（每周至少2次，假设周二和周五）
            weekday = current.weekday()  # 0=周一, 1=周二, ...
            if weekday in [1, 4]:  # 周二和周五
                records.append({
                    "date": current.strftime("%Y-%m-%d"),
                    "day": day,
                    "type": "主治医师查房记录"
                })

            # 主任医师查房记录（每周至少1次，假设周三）
            if weekday == 2:  # 周三
                records.append({
                    "date": current.strftime("%Y-%m-%d"),
                    "day": day,
                    "type": "主任医师查房记录"
                })

            # 阶段小结（每月一次，第30天、第60天、第90天）
            if day in [30, 60, 90]:
                records.append({
                    "date": current.strftime("%Y-%m-%d"),
                    "day": day,
                    "type": "阶段小结"
                })

            current += timedelta(days=1)
            day += 1

        return records
