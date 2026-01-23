"""
AI服务管理器
"""
from typing import Optional
from ai_services.base_service import AIService
from ai_services.modelscope_service import ModelScopeService
from ai_services.deepseek_service import DeepSeekService
from ai_services.kimi_service import KimiService
from ai_services.siliconflow_embedder import SiliconFlowEmbedder


class AIServiceManager:
    """AI服务管理器"""

    def __init__(self, config: dict):
        """初始化AI服务管理器

        Args:
            config: 配置字典，包含ai_services配置
        """
        self.services = {}
        self.default_service = None
        self.embedder = None

        # 初始化嵌入服务
        siliconflow_config = config.get("siliconflow", {})
        if siliconflow_config.get("api_key"):
            self.embedder = SiliconFlowEmbedder(
                api_key=siliconflow_config["api_key"]
            )

        # 初始化AI服务
        ai_config = config.get("ai_services", {})
        for provider, settings in ai_config.items():
            if provider == "default":
                continue

            if settings.get("api_key"):
                service_class = self._get_service_class(provider)
                self.services[provider] = service_class(
                    api_key=settings["api_key"],
                    model=settings.get("model")
                )

                if settings.get("is_default") or ai_config.get("default") == provider:
                    self.default_service = provider

    def get_service(self, provider: str = None) -> Optional[AIService]:
        """获取AI服务实例

        Args:
            provider: 服务商名称，默认使用default服务

        Returns:
            AI服务实例
        """
        if provider is None:
            provider = self.default_service

        return self.services.get(provider)

    def get_embedder(self) -> Optional[SiliconFlowEmbedder]:
        """获取嵌入服务"""
        return self.embedder

    def _get_service_class(self, provider: str):
        """根据服务商名称返回对应的类"""
        service_map = {
            "modelscope": ModelScopeService,
            "deepseek": DeepSeekService,
            "kimi": KimiService
        }
        return service_map.get(provider)
