"""
主窗口 - iOS风格
"""
import customtkinter as ctk
from ui.styles import Colors


class MainWindow(ctk.CTk):
    """主窗口类"""

    def __init__(self, db_manager, ai_manager, kb_manager):
        super().__init__()

        self.db = db_manager
        self.ai = ai_manager
        self.kb = kb_manager
        self.current_patient = None

        # 配置窗口
        self.title("康复科助手")
        self.geometry("1400x900")

        # 配置网格布局
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 创建界面
        self._create_navbar()
        self._create_sidebar()
        self._create_workspace()
        self._create_quick_tools()

    def _create_navbar(self):
        """创建顶部导航栏"""
        navbar = ctk.CTkFrame(self, height=60, fg_color="transparent")
        navbar.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

        # 左侧：应用图标和标题
        left_frame = ctk.CTkFrame(navbar, fg_color="transparent")
        left_frame.pack(side="left", padx=10)

        ctk.CTkLabel(left_frame, text="🏥", font=ctk.CTkFont(size=24)).pack(side="left")
        ctk.CTkLabel(left_frame, text="康复科助手", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=10)

        # 中间：日期
        center_frame = ctk.CTkFrame(navbar, fg_color="transparent")
        center_frame.pack(side="left", expand=True)
        # TODO: 添加日期显示

        # 右侧：按钮
        right_frame = ctk.CTkFrame(navbar, fg_color="transparent")
        right_frame.pack(side="right", padx=10)

        # 提醒按钮
        self.reminder_btn = ctk.CTkButton(
            right_frame,
            text="🔔 5",
            width=50,
            fg_color="transparent",
            border_width=2
        )
        self.reminder_btn.pack(side="left", padx=5)

        # 新患者按钮
        new_patient_btn = ctk.CTkButton(
            right_frame,
            text="➕ 新患者",
            fg_color=Colors.PRIMARY
        )
        new_patient_btn.pack(side="left", padx=5)

        # 设置按钮
        settings_btn = ctk.CTkButton(
            right_frame,
            text="⚙️",
            width=50,
            fg_color="transparent"
        )
        settings_btn.pack(side="left", padx=5)

    def _create_sidebar(self):
        """创建左侧患者列表"""
        sidebar = ctk.CTkFrame(self, width=280, corner_radius=12)
        sidebar.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # 标题
        header = ctk.CTkFrame(sidebar, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(header, text="今日待办", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        ctk.CTkLabel(header, text="12", font=ctk.CTkFont(size=18, weight="bold"), text_color=Colors.PRIMARY).pack(side="right")

        # 患者列表
        self.patient_list_frame = ctk.CTkScrollableFrame(sidebar, label_text="")
        self.patient_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # TODO: 加载患者列表

    def _create_workspace(self):
        """创建中间工作区"""
        workspace = ctk.CTkScrollableFrame(self, corner_radius=12)
        workspace.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # 患者信息卡片
        info_frame = ctk.CTkFrame(workspace)
        info_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(info_frame, text="患者信息", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=15, pady=10)

        # TODO: 添加患者详细信息

        # 病程记录生成卡片
        note_frame = ctk.CTkFrame(workspace)
        note_frame.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(note_frame, text="病程记录生成", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=15, pady=10)

        # 当日情况输入
        ctk.CTkLabel(note_frame, text="当日情况：", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=15)

        self.daily_condition_text = ctk.CTkTextbox(note_frame, height=100)
        self.daily_condition_text.pack(fill="x", padx=15, pady=5)

        # 操作按钮
        btn_frame = ctk.CTkFrame(note_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(
            btn_frame,
            text="✨ AI生成",
            fg_color=Colors.PRIMARY,
            command=self._on_generate_note
        ).pack(side="left", expand=True, fill="x", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="💾 保存",
            command=self._on_save_note
        ).pack(side="left", expand=True, fill="x", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="📄 导出txt",
            command=self._on_export_note
        ).pack(side="left", expand=True, fill="x", padx=5)

        # 预览区域
        ctk.CTkLabel(note_frame, text="AI生成预览：", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=15)

        self.preview_text = ctk.CTkTextbox(note_frame, height=200)
        self.preview_text.pack(fill="both", expand=True, padx=15, pady=5)

    def _create_quick_tools(self):
        """创建右侧快速工具"""
        tools = ctk.CTkFrame(self, width=300, corner_radius=12)
        tools.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(tools, text="快速模板", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=15, pady=15)

        # 模板选择器
        # TODO: 添加模板下拉框

        # 常用短语
        ctk.CTkLabel(tools, text="常用短语", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=15, pady=(10, 5))

        phrases_frame = ctk.CTkFrame(tools, fg_color="transparent")
        phrases_frame.pack(fill="x", padx=15)

        phrases = ["患者神志清，精神可", "继续康复训练", "家属配合", "查体同前"]
        for phrase in phrases:
            btn = ctk.CTkButton(
                phrases_frame,
                text=phrase,
                fg_color="transparent",
                border_width=1,
                anchor="w"
            )
            btn.pack(fill="x", pady=2)

    def _on_generate_note(self):
        """生成病程记录"""
        if not self.current_patient:
            ctk.CTkMessageBox(
                title="提示",
                message="请先选择患者",
                icon="warning"
            )
            return

        daily_condition = self.daily_condition_text.get("1.0", "end").strip()
        if not daily_condition:
            ctk.CTkMessageBox(
                title="提示",
                message="请输入当日情况",
                icon="warning"
            )
            return

        # TODO: 调用生成模块
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", "正在生成...")

    def _on_save_note(self):
        """保存病程记录"""
        # TODO: 实现保存功能
        pass

    def _on_export_note(self):
        """导出病程记录"""
        # TODO: 实现导出功能
        pass
