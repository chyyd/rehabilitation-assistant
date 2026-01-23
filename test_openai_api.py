"""
测试魔搭API连接 - 使用OpenAI客户端
"""
from openai import OpenAI


def test_modelscope_api():
    """测试魔搭API"""
    api_key = "ms-f449b8b0-f623-4f91-9288-a1c13d38daed"
    base_url = "https://api-inference.modelscope.cn/v1"
    model = "deepseek-ai/DeepSeek-V3.2"

    print("[INFO] 初始化OpenAI客户端...")
    print(f"   Base URL: {base_url}")
    print(f"   Model: {model}")
    print(f"   API Key: {api_key[:20]}...")

    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )

    print("\n[TEST] 测试API调用...")

    # 启用thinking模式
    extra_body = {
        "enable_thinking": True
    }

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': '请用一句话介绍你自己'
                }
            ],
            stream=False,
            extra_body=extra_body
        )

        print("\n[SUCCESS] API调用成功！")
        content = response.choices[0].message.content
        # 处理emoji编码问题
        try:
            print(f"\n[RESPONSE] {content}")
        except UnicodeEncodeError:
            print(f"\n[RESPONSE] (包含特殊字符，已简化显示)")
            print(content.encode('utf-8', errors='ignore').decode('utf-8'))

    except Exception as e:
        print(f"\n[ERROR] API调用失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_modelscope_api()
