"""
测试魔搭API连接
"""
import json
from ai_services import AIServiceManager


def load_config():
    """加载配置"""
    with open("config.json", 'r', encoding='utf-8') as f:
        return json.load(f)


def test_api():
    """测试API连接"""
    print("[INFO] 加载配置...")
    config = load_config()

    print("[INFO] 初始化AI服务...")
    ai_manager = AIServiceManager(config)

    print("[INFO] 获取魔搭服务...")
    service = ai_manager.get_service("modelscope")

    if not service:
        print("[ERROR] 服务未初始化")
        return

    print("[SUCCESS] 服务已加载")
    print(f"   - API密钥: {service.api_key[:20]}...")
    print(f"   - 模型: {service.model}")
    print(f"   - Base URL: {service.base_url}")

    print("\n[TEST] 测试API调用...")
    try:
        messages = [
            {"role": "system", "content": "你是一个专业的助手。"},
            {"role": "user", "content": "请简单介绍一下你自己，不超过50字。"}
        ]

        response = service._call_api(messages, temperature=0.7)
        print("[SUCCESS] API调用成功！")
        print(f"\n[RESPONSE] AI回复:\n{response}")

    except Exception as e:
        print(f"[ERROR] API调用失败: {str(e)}")


if __name__ == "__main__":
    test_api()
