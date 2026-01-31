"""
直接测试魔搭API网络连接
"""
import requests
import json


def test_direct_api():
    """直接测试API调用"""
    api_key = "ms-f449b8b0-f623-4f91-9288-a1c13d38daed"
    base_url = "https://api.modelscope.cn/v1"
    model = "deepseek-ai/DeepSeek-V3"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print(f"[TEST] Testing direct API call to {base_url}")
    print(f"[INFO] Model: {model}")
    print(f"[INFO] API Key: {api_key[:20]}...")

    messages = [
        {"role": "system", "content": "You are a professional assistant."},
        {"role": "user", "content": "Say hello in one sentence."}
    ]

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7
    }

    print(f"\n[REQUEST] Sending request...")
    print(f"Headers: {json.dumps({k: v[:20] + '...' if k == 'Authorization' else v for k, v in headers.items()}, indent=2)}")

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"\n[STATUS] HTTP Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"\n[SUCCESS] API call successful!")
            print(f"\n[RESPONSE] {content}")
        else:
            print(f"\n[ERROR] Request failed")
            print(f"Response: {response.text}")

    except requests.exceptions.Timeout:
        print(f"\n[ERROR] Request timeout (30s)")
    except requests.exceptions.ConnectionError as e:
        print(f"\n[ERROR] Connection error: {str(e)}")
        print(f"\n[TIPS] Possible causes:")
        print(f"  1. Network connection issue")
        print(f"  2. Firewall blocking the connection")
        print(f"  3. API server unavailable")
        print(f"  4. Invalid API endpoint")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")


if __name__ == "__main__":
    test_direct_api()
