"""
AI服务抽象基类
"""
from abc import ABC, abstractmethod


class AIService(ABC):
    """AI服务抽象基类"""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    @abstractmethod
    def extract_patient_info(self, initial_note: str) -> dict:
        """从首次病程记录提取患者信息"""
        pass

    @abstractmethod
    def generate_progress_note(self, context: dict) -> str:
        """生成病程记录"""
        pass

    @abstractmethod
    def generate_rehab_plan(self, patient_info: dict) -> dict:
        """生成康复计划"""
        pass

    def _call_api(self, messages: list, temperature: float = 0.7) -> str:
        """调用AI API的通用方法（子类需实现）"""
        pass
