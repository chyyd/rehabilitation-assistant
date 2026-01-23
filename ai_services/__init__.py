"""
AI服务模块初始化
"""
from ai_services.base_service import AIService
from ai_services.modelscope_service import ModelScopeService
from ai_services.deepseek_service import DeepSeekService
from ai_services.kimi_service import KimiService
from ai_services.siliconflow_embedder import SiliconFlowEmbedder
from ai_services.service_manager import AIServiceManager

__all__ = [
    'AIService',
    'ModelScopeService',
    'DeepSeekService',
    'KimiService',
    'SiliconFlowEmbedder',
    'AIServiceManager'
]
