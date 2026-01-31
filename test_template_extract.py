"""
测试模板提取功能
"""
import requests

# 测试数据
test_content = """
患者张三，男，65岁，因脑梗塞入院。
主要症状：左侧肢体无力，言语不清。
查体：血压150/90mmHg，心率78次/分，双肺呼吸音清。
治疗方案：抗血小板聚集，改善脑循环，营养神经。
康复训练：肢体功能训练，言语训练。
"""

print("测试模板提取功能...")
print("=" * 60)

try:
    response = requests.post(
        'http://127.0.0.1:8000/api/templates/extract-phrases',
        json={
            'content': test_content,
            'filename': 'test.md'
        },
        timeout=30
    )

    print(f"\n状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ 提取成功!")
        print(f"提取的语句数量: {len(data.get('phrases', []))}")
        print(f"\n消息: {data.get('message', 'N/A')}")

        if data.get('phrases'):
            print("\n提取的语句:")
            for i, phrase in enumerate(data['phrases'][:5], 1):  # 只显示前5条
                print(f"{i}. [{phrase.get('category', '未分类')}] {phrase.get('content', '')[:50]}...")
    else:
        print(f"\n❌ 请求失败")
        print(f"错误详情: {response.text}")

except requests.exceptions.ConnectionError:
    print("\n❌ 无法连接到后端服务")
    print("   请确认后端已启动: python main.py")
except Exception as e:
    print(f"\n❌ 测试失败: {e}")

print("\n" + "=" * 60)
