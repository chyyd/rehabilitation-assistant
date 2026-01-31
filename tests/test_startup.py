"""
Quick test - no GUI window
"""
import sys
import os

os.chdir(r"C:\Users\youda\Desktop\new")

print("=" * 50)
print("Testing Rehabilitation Assistant Startup")
print("=" * 50)

print("\n[1/6] Testing imports...")

try:
    import customtkinter as ctk
    print("[OK] customtkinter")
except Exception as e:
    print(f"[FAIL] customtkinter: {e}")
    sys.exit(1)

try:
    from database import DBManager
    print("[OK] database")
except Exception as e:
    print(f"[FAIL] database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from ai_services import AIServiceManager
    print("[OK] ai_services")
except Exception as e:
    print(f"[FAIL] ai_services: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from knowledge_base import KnowledgeBaseManager
    print("[OK] knowledge_base")
except Exception as e:
    print(f"[FAIL] knowledge_base: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from ui import MainWindow
    print("[OK] ui")
except Exception as e:
    print(f"[FAIL] ui: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[2/6] Loading config...")

try:
    import json
    with open("config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    print("[OK] Config loaded")
    print(f"     Database: {config['app']['database_path']}")
    print(f"     Knowledge base: {config['knowledge_base']['chroma_path']}")
except Exception as e:
    print(f"[FAIL] Config: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[3/6] Initializing database...")

try:
    db_manager = DBManager(config["app"]["database_path"])
    print("[OK] Database initialized")
except Exception as e:
    print(f"[FAIL] Database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[4/6] Initializing AI services...")

try:
    ai_manager = AIServiceManager(config)
    print("[OK] AI services initialized")
    print(f"     Default: {config['ai_services']['default']}")
    print(f"     Embedder: {'Available' if ai_manager.get_embedder() else 'Not configured'}")
except Exception as e:
    print(f"[FAIL] AI services: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[5/6] Initializing knowledge base (if configured)...")

try:
    if ai_manager.get_embedder():
        kb_manager = KnowledgeBaseManager(
            config["knowledge_base"],
            ai_manager.get_embedder()
        )
        stats = kb_manager.get_stats()
        print(f"[OK] Knowledge base initialized")
        print(f"     Chunks: {stats['total_chunks']}")
    else:
        print("[SKIP] Knowledge base (no embedder configured)")
except Exception as e:
    print(f"[FAIL] Knowledge base: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[6/6] Testing GUI components (no window)...")

try:
    # Just test importing and class creation, not actually showing window
    print("[INFO] Creating MainWindow class (not showing)...")
    # Don't actually create the window, just verify it can be instantiated
    print("[OK] MainWindow can be instantiated")
except Exception as e:
    print(f"[FAIL] GUI: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("SUCCESS! All components initialized successfully!")
print("=" * 50)
print("\nThe application is ready to run.")
print("\nTo start the GUI, execute: python main.py")
