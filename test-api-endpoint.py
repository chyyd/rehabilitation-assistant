"""
测试新增的AI服务端点
运行此脚本验证 /api/ai/test 和 /api/ai/test-embedding 是否可用
"""
import requests
import json
import sys
import io

# 修复Windows控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def test_ai_endpoint():
    """测试AI服务连接端点"""
    print("=" * 60)
    print("测试 POST /api/ai/test")
    print("=" * 60)

    url = f"{BASE_URL}/api/ai/test"
    payload = {
        "service": "deepseek",
        "api_key": "sk-test-key",
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat"
    }

    print(f"\n请求URL: {url}")
    print(f"请求数据: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            print("\n✅ 端点测试成功！")
            return True
        elif response.status_code == 404:
            print("\n❌ 端点不存在（404）")
            print("   请检查后端是否已重启并加载了最新代码")
            return False
        else:
            print(f"\n⚠️  端点返回错误: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到后端服务")
        print("   请确认后端服务已启动: python main.py")
        return False
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False

def test_embedding_endpoint():
    """测试Embedding服务连接端点"""
    print("\n" + "=" * 60)
    print("测试 POST /api/ai/test-embedding")
    print("=" * 60)

    url = f"{BASE_URL}/api/ai/test-embedding"
    payload = {
        "service": "siliconflow",
        "api_key": "sk-test-key",
        "base_url": "https://api.siliconflow.cn/v1",
        "model": "BAAI/bge-large-zh-v1.5"
    }

    print(f"\n请求URL: {url}")
    print(f"请求数据: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            print("\n✅ 端点测试成功！")
            return True
        elif response.status_code == 404:
            print("\n❌ 端点不存在（404）")
            return False
        else:
            print(f"\n⚠️  端点返回错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False

def check_openapi():
    """检查OpenAPI文档中是否包含测试端点"""
    print("\n" + "=" * 60)
    print("检查 OpenAPI 文档")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi = response.json()
            paths = openapi.get("paths", {})

            test_endpoints = [p for p in paths.keys() if "test" in p]

            print(f"\n找到的包含'test'的端点:")
            for endpoint in test_endpoints:
                print(f"  - {endpoint}")

            if "/api/ai/test" in paths:
                print("\n✅ /api/ai/test 端点已注册")
            else:
                print("\n❌ /api/ai/test 端点未找到")

            if "/api/ai/test-embedding" in paths:
                print("✅ /api/ai/test-embedding 端点已注册")
            else:
                print("❌ /api/ai/test-embedding 端点未找到")

            return len(test_endpoints) > 0
        else:
            print(f"\n❌ 无法获取OpenAPI文档: {response.status_code}")
            return False
    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  AI服务测试端点验证工具")
    print("=" * 60)

    # 先检查OpenAPI文档
    api_check = check_openapi()

    # 如果端点已注册，测试实际调用
    if api_check:
        print("\n" + "=" * 60)
        print("端点已注册，测试实际调用...")
        print("=" * 60)

        test_ai_endpoint()
        test_embedding_endpoint()
    else:
        print("\n" + "=" * 60)
        print("端点未注册，请检查后端代码")
        print("=" * 60)

    print("\n" + "=" * 60)
    print("  测试完成")
    print("=" * 60)
