"""
数据库测试
"""
import pytest
import tempfile
import os
from database import DBManager, Patient


def test_add_patient(db_manager):
    """测试添加患者"""
    patient_data = {
        "hospital_number": "TEST001",
        "name": "测试患者",
        "gender": "男",
        "age": 65,
        "admission_date": "2025-01-23",
        "diagnosis": "脑梗死恢复期",
        "initial_note": "患者因右侧肢体活动不利10天入院..."
    }

    patient_id = db_manager.add_patient(patient_data)
    assert patient_id is not None

    # 验证患者已添加
    patient = db_manager.get_patient_by_hospital_number("TEST001")
    assert patient is not None
    assert patient.name == "测试患者"


@pytest.fixture
def db_manager():
    """数据库管理器fixture"""
    # 使用临时数据库
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()

    db = DBManager(temp_db.name)

    yield db

    # 清理
    os.unlink(temp_db.name)
