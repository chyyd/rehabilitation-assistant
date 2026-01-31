"""
Test script - diagnose main.py issues step by step
"""
import sys

print("Step 1: Testing imports...")

try:
    import customtkinter as ctk
    print("[OK] customtkinter imported")
except Exception as e:
    print(f"[FAIL] customtkinter failed: {e}")
    sys.exit(1)

try:
    print("\nStep 2: Testing database imports...")
    from database import DBManager
    print("[OK] database imported")
except Exception as e:
    print(f"[FAIL] database failed: {e}")
    sys.exit(1)

try:
    print("\nStep 3: Testing AI services imports...")
    from ai_services import AIServiceManager
    print("[OK] ai_services imported")
except Exception as e:
    print(f"[FAIL] ai_services failed: {e}")
    sys.exit(1)

try:
    print("\nStep 4: Testing knowledge base imports...")
    from knowledge_base import KnowledgeBaseManager
    print("[OK] knowledge_base imported")
except Exception as e:
    print(f"[FAIL] knowledge_base failed: {e}")
    sys.exit(1)

try:
    print("\nStep 5: Testing UI imports...")
    from ui import MainWindow
    print("[OK] ui imported")
except Exception as e:
    print(f"[FAIL] ui failed: {e}")
    sys.exit(1)

try:
    print("\nStep 6: Loading config...")
    import json
    with open("config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"[OK] config loaded")
    print(f"  - Database: {config['app']['database_path']}")
except Exception as e:
    print(f"[FAIL] config failed: {e}")
    sys.exit(1)

try:
    print("\nStep 7: Initializing database...")
    db_manager = DBManager(config["app"]["database_path"])
    print("[OK] Database initialized")
except Exception as e:
    print(f"[FAIL] Database failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\nStep 8: Initializing AI services...")
    ai_manager = AIServiceManager(config)
    print("[OK] AI services initialized")
except Exception as e:
    print(f"[FAIL] AI services failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[SUCCESS] All basic checks passed!")
print("\nNow trying to create a minimal test window...")

try:
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.geometry("400x300")
    app.title("Test Window")

    label = ctk.CTkLabel(app, text="Rehabilitation Assistant - Test", font=ctk.CTkFont(size=20, weight="bold"))
    label.pack(padx=20, pady=20)

    button = ctk.CTkButton(app, text="Close", command=app.destroy)
    button.pack(padx=20, pady=10)

    print("Test window created successfully!")
    print("Close the window to continue...")

    app.mainloop()

    print("Window closed successfully!")

except Exception as e:
    print(f"[FAIL] GUI failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[SUCCESS] All tests passed!")
