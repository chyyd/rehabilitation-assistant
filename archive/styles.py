"""
UI样式配置 - iOS风格
"""
import customtkinter as ctk

# 颜色定义
class Colors:
    PRIMARY = "#007AFF"
    SUCCESS = "#34C759"
    WARNING = "#FF9500"
    DANGER = "#FF3B30"
    BACKGROUND = "#F2F2F7"
    CARD = "#FFFFFF"

# 字体配置
class Fonts:
    @staticmethod
    def init_fonts():
        """初始化字体（在main.py中调用）"""
        return {
            'TITLE_LARGE': ctk.CTkFont(size=24, weight="bold"),
            'TITLE_MEDIUM': ctk.CTkFont(size=18, weight="bold"),
            'BODY': ctk.CTkFont(size=14),
            'SMALL': ctk.CTkFont(size=12)
        }
