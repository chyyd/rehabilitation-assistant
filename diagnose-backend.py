"""
后端服务诊断工具
检查后端是否正确加载了修复后的代码
"""
import subprocess
import time
import requests
import sys

def check_python_processes():
    """检查Python进程"""
    print("=" * 60)
    print("检查Python进程")
    print("=" * 60)

    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName | Format-Table"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(result.stdout)
        if "python" in result.stdout:
            print("⚠️  发现Python进程正在运行")
            return True
        else:
            print("✅ 没有Python进程运行")
            return False
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def kill_python_processes():
    """停止所有Python进程"""
    print("\n" + "=" * 60)
    print("停止所有Python进程")
    print("=" * 60)

    try:
        subprocess.run(
            ["powershell", "-Command", "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"],
            capture_output=True,
            timeout=10
        )
        print("✅ 已停止所有Python进程")
        time.sleep(2)
    except Exception as e:
        print(f"⚠️  停止进程时出现警告: {e}")

def check_api_endpoints():
    """检查API端点"""
    print("\n" + "=" * 60)
    print("检查API端点")
    print("=" * 60)

    try:
        response = requests.get("http://127.0.0.1:8000/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi = response.json()
            paths = openapi.get("paths", {})

            print(f"\n✅ 后端服务运行正常")
            print(f"总共有 {len(paths)} 个端点\n")

            # 检查测试端点
            test_endpoints = [p for p in paths.keys() if "test" in p]
            if test_endpoints:
                print("测试端点:")
                for endpoint in test_endpoints:
                    print(f"  ✓ {endpoint}")
            else:
                print("⚠️  没有找到测试端点")

            # 检查模板端点
            template_endpoints = [p for p in paths.keys() if "template" in p]
            if template_endpoints:
                print("\n模板端点:")
                for endpoint in template_endpoints:
                    print(f"  ✓ {endpoint}")

            return True
        else:
            print(f"❌ 后端响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务 (http://127.0.0.1:8000)")
        print("   后端服务可能未启动")
        return False
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def check_code_fix():
    """检查代码是否已修复"""
    print("\n" + "=" * 60)
    print("检查代码修复状态")
    print("=" * 60)

    files_to_check = [
        ("backend/api/routes/ai.py", "ai.py"),
        ("backend/api/routes/templates.py", "templates.py")
    ]

    all_fixed = True
    for filepath, filename in files_to_check:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            if "get_default_service()" in content:
                print(f"❌ {filename}: 仍然包含错误的方法名")
                all_fixed = False
            elif "get_service()" in content:
                print(f"✅ {filename}: 已修复")
            else:
                print(f"⚠️  {filename}: 未找到相关方法调用")
        except FileNotFoundError:
            print(f"❌ {filename}: 文件不存在")
            all_fixed = False
        except Exception as e:
            print(f"❌ {filename}: 检查失败 - {e}")
            all_fixed = False

    return all_fixed

def main():
    print("\n" + "=" * 60)
    print("  后端服务诊断工具")
    print("=" * 60)

    # 1. 检查代码是否已修复
    code_fixed = check_code_fix()

    if not code_fixed:
        print("\n❌ 代码未修复，请先运行修复命令")
        print("   运行: git pull 或重新应用修复")
        return

    # 2. 检查是否有Python进程运行
    has_python = check_python_processes()

    # 3. 如果有进程，建议停止
    if has_python:
        print("\n⚠️  检测到Python进程正在运行")
        print("   这些进程可能正在运行旧代码")
        response = input("\n是否停止所有Python进程? (y/n): ")

        if response.lower() == 'y':
            kill_python_processes()
            print("\n✅ 进程已停止")
            print("   请重新启动后端: python main.py")
        else:
            print("\n⚠️  继续使用当前进程可能导致错误")
    else:
        print("\n✅ 没有Python进程运行")
        print("   请启动后端: python main.py")

    # 4. 检查API端点
    print("\n检查后端服务状态...")
    api_ok = check_api_endpoints()

    if api_ok:
        print("\n" + "=" * 60)
        print("✅ 后端服务状态良好")
        print("=" * 60)
        print("\n现在可以使用以下功能:")
        print("  1. 多文件上传")
        print("  2. 批量分析")
        print("  3. 模板提取")
    else:
        print("\n" + "=" * 60)
        print("❌ 后端服务未运行或有问题")
        print("=" * 60)
        print("\n请执行以下步骤:")
        print("  1. 运行: .\\restart-backend.ps1")
        print("  2. 或手动启动: python main.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)
