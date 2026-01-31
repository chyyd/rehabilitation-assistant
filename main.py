"""
康复科助手 - 后端API服务启动器
启动FastAPI后端服务为Electron前端提供API
"""
import subprocess
import sys
import os

# 切换到项目根目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("   康复科助手 - 后端API服务")
print("=" * 60)
print()
print("正在启动FastAPI后端服务...")
print("API文档: http://127.0.0.1:8000/docs")
print("API根路径: http://127.0.0.1:8000/")
print()
print("按 Ctrl+C 停止服务")
print("=" * 60)
print()

# 启动FastAPI服务
subprocess.run([
    sys.executable, "-m", "uvicorn",
    "backend.api_main:app",
    "--host", "127.0.0.1",
    "--port", "8000",
    "--reload"
])
