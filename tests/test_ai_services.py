"""
AI服务测试
"""
import pytest
from ai_services import AIServiceManager


def test_service_manager_initialization():
    """测试AI服务管理器初始化"""
    config = {
        "siliconflow": {
            "api_key": "test_key"
        },
        "ai_services": {
            "default": "modelscope",
            "modelscope": {
                "api_key": "",
                "model": "Qwen2.5-72B-Instruct"
            }
        }
    }

    manager = AIServiceManager(config)
    assert manager is not None
    assert manager.get_embedder() is not None
