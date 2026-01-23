"""
康复科助手 - 主入口
"""
import customtkinter as ctk
import json
from pathlib import Path

from database import DBManager
from ai_services import AIServiceManager
from knowledge_base import KnowledgeBaseManager
from ui import MainWindow


def load_config(config_path: str = "config.json") -> dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    # 配置CustomTkinter
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")

    # 加载配置
    config = load_config()

    # 初始化数据库
    print("初始化数据库...")
    db_manager = DBManager(config["app"]["database_path"])

    # 初始化AI服务
    print("初始化AI服务...")
    ai_manager = AIServiceManager(config)

    # 初始化知识库
    kb_manager = None
    if ai_manager.get_embedder():
        print("初始化知识库...")
        kb_manager = KnowledgeBaseManager(
            config["knowledge_base"],
            ai_manager.get_embedder()
        )

    # 创建并运行主窗口
    print("启动应用...")
    app = MainWindow(db_manager, ai_manager, kb_manager)
    app.mainloop()


if __name__ == "__main__":
    main()
