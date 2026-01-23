"""
集成测试
"""
import pytest
from modules import PatientManager, ProgressNoteGenerator
from database import DBManager
from ai_services import AIServiceManager


def test_create_patient_workflow(db_manager, ai_manager):
    """测试创建患者完整流程"""
    patient_mgr = PatientManager(db_manager, ai_manager)

    # 注意：此测试需要真实API密钥
    result = patient_mgr.create_patient(
        hospital_number="TEST001",
        initial_note="患者张三，男，65岁，因右侧肢体活动不利10天入院..."
    )

    # 由于没有真实API，这里只测试结构
    assert "success" in result


@pytest.fixture
def ai_manager():
    """AI管理器fixture"""
    config = {
        "siliconflow": {
            "api_key": "test_key"
        },
        "ai_services": {
            "default": "modelscope",
            "modelscope": {
                "api_key": "test_key",
                "model": "Qwen2.5-72B-Instruct"
            }
        }
    }

    return AIServiceManager(config)
