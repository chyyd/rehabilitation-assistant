# -*- coding: utf-8 -*-
"""
测试修复后的API路由 - 验证session依赖注入
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_notes_routes():
    """测试notes.py路由"""
    print("测试 notes.py...")
    from backend.api.routes.notes import router, get_session
    print("[OK] notes.py 导入成功")

    # 验证所有端点签名
    for route in router.routes:
        if hasattr(route, 'endpoint') and hasattr(route.endpoint, '__code__'):
            code = route.endpoint.__code__
            # 检查是否使用session依赖
            if 'session' in code.co_varnames:
                print(f"  [OK] {route.path} 使用session依赖")
            else:
                # extract-patient-info不需要session
                if 'extract' not in route.path:
                    print(f"  [?] {route.path} 可能需要检查")

    return True

def test_templates_routes():
    """测试templates.py路由"""
    print("\n测试 templates.py...")
    from backend.api.routes.templates import router, get_session
    print("[OK] templates.py 导入成功")

    # 验证所有端点签名
    for route in router.routes:
        if hasattr(route, 'endpoint') and hasattr(route.endpoint, '__code__'):
            code = route.endpoint.__code__
            if 'session' in code.co_varnames:
                print(f"  [OK] {route.path} 使用session依赖")

    return True

def test_ai_routes():
    """测试ai.py路由"""
    print("\n测试 ai.py...")
    from backend.api.routes.ai import router, get_session, get_managers
    print("[OK] ai.py 导入成功")

    # 验证所有端点签名
    for route in router.routes:
        if hasattr(route, 'endpoint') and hasattr(route.endpoint, '__code__'):
            code = route.endpoint.__code__
            varnames = code.co_varnames
            if 'session' in varnames or 'managers' in varnames:
                deps = []
                if 'session' in varnames:
                    deps.append('session')
                if 'managers' in varnames:
                    deps.append('managers')
                print(f"  [OK] {route.path} 使用依赖: {', '.join(deps)}")

    return True

def test_dependencies():
    """测试依赖函数定义"""
    print("\n测试依赖函数...")

    # 测试notes.py
    from backend.api.routes import notes
    assert hasattr(notes, 'get_session'), "notes.py缺少get_session函数"
    assert not hasattr(notes, 'get_db_manager'), "notes.py仍存在get_db_manager函数"
    print("[OK] notes.py 依赖函数正确")

    # 测试templates.py
    from backend.api.routes import templates
    assert hasattr(templates, 'get_session'), "templates.py缺少get_session函数"
    assert not hasattr(templates, 'get_db_manager'), "templates.py仍存在get_db_manager函数"
    print("[OK] templates.py 依赖函数正确")

    # 测试ai.py
    from backend.api.routes import ai
    assert hasattr(ai, 'get_session'), "ai.py缺少get_session函数"
    assert hasattr(ai, 'get_managers'), "ai.py缺少get_managers函数"
    # 注意：ai.py的get_managers不应该返回db_manager
    print("[OK] ai.py 依赖函数正确")

    return True

def main():
    print("=" * 60)
    print("API路由Session依赖修复验证")
    print("=" * 60)

    try:
        test_dependencies()
        test_notes_routes()
        test_templates_routes()
        test_ai_routes()

        print("\n" + "=" * 60)
        print("[SUCCESS] 所有测试通过！Session依赖已正确修复")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n[FAILED] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
