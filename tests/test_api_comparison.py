"""
对比Demo版本和新版本API的响应差异
"""
import json
import requests
from database import DBManager
from datetime import datetime

def compare_responses():
    db = DBManager('./rehab_assistant.db')

    # 获取Demo版本数据
    demo_patients = db.get_all_patients(include_discharged=False)

    # 获取API版本数据
    try:
        response = requests.get('http://127.0.0.1:8000/api/patients/')
        api_patients = response.json()
    except Exception as e:
        print(f"无法连接到API: {e}")
        return

    print("=" * 80)
    print("Demo版本 vs 新版本API 响应对比")
    print("=" * 80)

    # 对比每个患者
    for demo_p in demo_patients[:2]:  # 只对比前2个
        # 找到对应的API数据
        api_p = next((p for p in api_patients if p['hospital_number'] == demo_p.hospital_number), None)

        if not api_p:
            print(f"\n❌ 患者 {demo_p.hospital_number} 在API响应中未找到！")
            continue

        print(f"\n患者: {demo_p.name} ({demo_p.hospital_number})")
        print("-" * 80)

        # 字段对比
        fields_to_compare = [
            'id', 'hospital_number', 'name', 'gender', 'age',
            'admission_date', 'discharge_date', 'diagnosis',
            'chief_complaint', 'days_in_hospital'
        ]

        differences = []
        for field in fields_to_compare:
            demo_value = getattr(demo_p, field, None)
            api_value = api_p.get(field)

            # 特殊处理日期字段
            if field == 'admission_date' and demo_value:
                demo_value = str(demo_value)

            # 特殊处理days_in_hospital
            if field == 'days_in_hospital':
                demo_calc = (datetime.now().date() - demo_p.admission_date).days
                demo_value = demo_calc

            # 对比
            if demo_value != api_value:
                differences.append({
                    'field': field,
                    'demo': demo_value,
                    'api': api_value
                })

        if differences:
            print("\n⚠️  发现差异:")
            for diff in differences:
                print(f"  字段: {diff['field']}")
                print(f"    Demo: {diff['demo']}")
                print(f"    API:  {diff['api']}")
        else:
            print("\n✅ 完全一致")

        # 检查API是否返回了额外字段
        api_fields = set(api_p.keys())
        expected_fields = set(fields_to_compare)
        extra_fields = api_fields - expected_fields

        if extra_fields:
            print(f"\nℹ️  API额外字段: {extra_fields}")

        # 检查API是否缺少字段
        missing_fields = expected_fields - api_fields
        if missing_fields:
            print(f"\n❌ API缺少字段: {missing_fields}")

    print("\n" + "=" * 80)

    # 测试单个患者API
    print("\n单个患者API测试:")
    test_hospital_number = demo_patients[0].hospital_number

    try:
        response = requests.get(f'http://127.0.0.1:8000/api/patients/{test_hospital_number}')
        if response.status_code == 200:
            patient_data = response.json()
            print(f"✅ GET /api/patients/{test_hospital_number} 成功")
            print(f"   返回字段: {list(patient_data.keys())}")
        else:
            print(f"❌ GET /api/patients/{test_hospital_number} 失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API调用失败: {e}")

if __name__ == '__main__':
    compare_responses()
