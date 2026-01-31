"""
改进的主窗口 - 功能完整版本
"""
import customtkinter as ctk
from datetime import datetime, date
from typing import Optional
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import os

from database import DBManager
from ai_services import AIServiceManager
from database.models import Patient, ProgressNote, Reminder


class ImprovedMainWindow(ctk.CTk):
    """改进的主窗口类 - 完整功能实现"""

    def __init__(self, db_manager: DBManager = None, ai_manager: AIServiceManager = None):
        super().__init__()

        # 保存管理器引用
        self.db_manager = db_manager or DBManager("./rehab_assistant.db")
        self.ai_manager = ai_manager

        # 当前选中的患者
        self.current_patient: Optional[Patient] = None

        # 配置窗口
        self.title("康复科助手")
        self.geometry("1400x900")
        self.configure(fg_color="#F2F2F7")  # iOS浅灰背景

        # 创建界面
        self._create_navbar()
        self._create_main_content()

        # 加载数据
        self._load_patients()

    def _create_navbar(self):
        """创建顶部导航栏"""
        navbar = ctk.CTkFrame(self, height=60, fg_color=("gray78", "gray78"), corner_radius=0)
        navbar.pack(fill="x", padx=0, pady=0)
        navbar.pack_propagate(False)

        # 左侧：应用图标和标题
        left_frame = ctk.CTkFrame(navbar, fg_color="transparent")
        left_frame.pack(side="left", padx=20)

        title_label = ctk.CTkLabel(
            left_frame,
            text="康复科助手",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white",
            anchor="w"
        )
        title_label.pack(side="left", padx=(0, 10))

        # 中间：日期
        center_frame = ctk.CTkFrame(navbar, fg_color="transparent")
        center_frame.pack(side="left", expand=True, fill="x")

        date_label = ctk.CTkLabel(
            center_frame,
            text=datetime.now().strftime("%Y年%m月%d日 %A"),
            font=ctk.CTkFont(size=14),
            text_color="white"
        )
        date_label.pack()

        # 右侧：按钮
        right_frame = ctk.CTkFrame(navbar, fg_color="transparent")
        right_frame.pack(side="right", padx=20)

        # 提醒按钮
        self.reminder_btn = ctk.CTkButton(
            right_frame,
            text="🔔 0",
            width=50,
            height=40,
            fg_color="transparent",
            border_width=2,
            border_color="white",
            text_color="white",
            command=self._show_reminders
        )
        self.reminder_btn.pack(side="left", padx=5)

        # 新患者按钮
        new_patient_btn = ctk.CTkButton(
            right_frame,
            text="➕ 新患者",
            height=40,
            fg_color="#007AFF",
            hover_color="#0051D5",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._show_new_patient_dialog
        )
        new_patient_btn.pack(side="left", padx=5)

        # 设置按钮
        settings_btn = ctk.CTkButton(
            right_frame,
            text="⚙️",
            width=50,
            height=40,
            fg_color="transparent",
            border_width=2,
            border_color="white",
            text_color="white"
        )
        settings_btn.pack(side="left", padx=5)

    def _create_main_content(self):
        """创建主内容区域"""
        # 主容器
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 三栏布局容器
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # 配置三栏
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # 左栏：患者列表（280px）
        self.left_sidebar = ctk.CTkScrollableFrame(
            content_frame,
            width=280,
            label_text="",
            fg_color="transparent"
        )
        self.left_sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # 中栏：工作区（flex）
        self.workspace = ctk.CTkScrollableFrame(
            content_frame,
            label_text="",
            fg_color="transparent"
        )
        self.workspace.grid(row=0, column=1, sticky="nsew", padx=5)

        # 右栏：快速工具（300px）
        self.right_sidebar = ctk.CTkFrame(
            content_frame,
            width=300,
            fg_color="transparent"
        )
        self.right_sidebar.grid(row=0, column=2, sticky="nsew", padx=(5, 0))

        # 创建各栏内容
        self._create_left_sidebar()
        self._create_workspace()
        self._create_right_sidebar()

    def _create_left_sidebar(self):
        """创建左侧患者列表"""
        # 标题栏
        header_frame = ctk.CTkFrame(self.left_sidebar, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        title = ctk.CTkLabel(
            header_frame,
            text="今日待办",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        title.pack(side="left")

        self.patient_count_label = ctk.CTkLabel(
            header_frame,
            text="0",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#007AFF",
            anchor="w"
        )
        self.patient_count_label.pack(side="right")

        # 患者列表容器
        self.patient_list_frame = ctk.CTkFrame(self.left_sidebar, fg_color="transparent")
        self.patient_list_frame.pack(fill="both", expand=True)

    def _create_workspace(self):
        """创建中间工作区"""
        # 提示信息（当没有选中患者时）
        self.empty_state_label = ctk.CTkLabel(
            self.workspace,
            text="请从左侧选择一个患者",
            font=ctk.CTkFont(size=16),
            text_color="#999999"
        )
        self.empty_state_label.pack(expand=True)

        # 患者信息卡片（初始隐藏）
        self.info_frame = None
        self.task_frame = None
        self.note_frame = None

    def _create_right_sidebar(self):
        """创建右侧快速工具栏"""
        # 标题
        title = ctk.CTkLabel(
            self.right_sidebar,
            text="快速模板",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        title.pack(anchor="w", pady=(0, 15))

        # 模板选择器
        self._create_template_selectors()

        # 常用短语
        self._create_common_phrases()

    def _create_template_selectors(self):
        """创建模板选择器"""
        selectors_frame = ctk.CTkFrame(self.right_sidebar, fg_color="transparent")
        selectors_frame.pack(fill="x", pady=(0, 15))

        # 诊断模板
        ctk.CTkLabel(selectors_frame, text="诊断模板:", anchor="w").pack(anchor="w")
        self.diagnosis_combo = ctk.CTkComboBox(
            selectors_frame,
            values=["选择诊断...", "脑梗死恢复期", "脊髓损伤恢复期", "颅脑损伤恢复期"],
            dropdown_fg_color="white",
            dropdown_hover_color="#F2F2F7",
            command=self._on_diagnosis_selected
        )
        self.diagnosis_combo.pack(fill="x", pady=(0, 10))

        # 处理意见模板
        ctk.CTkLabel(selectors_frame, text="处理意见:", anchor="w").pack(anchor="w")
        self.treatment_combo = ctk.CTkComboBox(
            selectors_frame,
            values=["选择处理...", "继续康复训练", "调整康复方案", "观察病情变化"],
            dropdown_fg_color="white",
            dropdown_hover_color="#F2F2F7",
            command=self._on_treatment_selected
        )
        self.treatment_combo.pack(fill="x", pady=(0, 10))

    def _create_common_phrases(self):
        """创建常用短语"""
        phrases_frame = ctk.CTkFrame(self.right_sidebar, fg_color="transparent")
        phrases_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(phrases_frame, text="常用短语:", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(anchor="w", pady=(0, 5))

        phrases = [
            "患者神志清，精神可",
            "继续康复训练",
            "家属配合",
            "查体同前"
        ]

        for phrase in phrases:
            btn = ctk.CTkButton(
                phrases_frame,
                text=phrase,
                height=35,
                fg_color="#F2F2F7",
                hover_color="#E5E5EA",
                text_color="#000000",
                anchor="w",
                font=ctk.CTkFont(size=12),
                command=lambda p=phrase: self._insert_phrase(p)
            )
            btn.pack(fill="x", pady=2)

    def _load_patients(self):
        """从数据库加载患者列表"""
        # 清空现有列表
        for widget in self.patient_list_frame.winfo_children():
            widget.destroy()

        # 从数据库获取患者
        patients = self.db_manager.get_all_patients(include_discharged=False)

        # 更新计数
        self.patient_count_label.configure(text=str(len(patients)))

        # 如果没有患者，添加一些示例数据
        if not patients:
            self._load_mock_patients()
            patients = self.db_manager.get_all_patients(include_discharged=False)

        # 添加患者卡片
        for patient in patients:
            self._add_patient_card(patient)

        # 更新提醒按钮
        reminders = self.db_manager.get_today_reminders()
        self.reminder_btn.configure(text=f"🔔 {len(reminders)}")

    def _load_mock_patients(self):
        """加载模拟患者数据到数据库"""
        from datetime import timedelta

        mock_patients = [
            {
                "hospital_number": "20241234",
                "name": "张三",
                "gender": "男",
                "age": 65,
                "admission_date": date.today() - timedelta(days=85),
                "diagnosis": "脑梗死恢复期"
            },
            {
                "hospital_number": "20241235",
                "name": "李四",
                "gender": "女",
                "age": 45,
                "admission_date": date.today() - timedelta(days=2),
                "diagnosis": "脊髓损伤恢复期"
            },
            {
                "hospital_number": "20241236",
                "name": "王五",
                "gender": "男",
                "age": 52,
                "admission_date": date.today() - timedelta(days=15),
                "diagnosis": "颅脑损伤恢复期"
            }
        ]

        for patient_data in mock_patients:
            existing = self.db_manager.get_patient_by_hospital_number(patient_data["hospital_number"])
            if not existing:
                self.db_manager.add_patient(patient_data)

    def _add_patient_card(self, patient: Patient):
        """添加患者卡片"""
        # 计算住院天数
        days = (date.today() - patient.admission_date).days

        # 确定优先级
        if days >= 85:
            priority = "urgent"
            priority_icon = "🚨"
            priority_color = "#FFF5F5"
            border_color = "#FF3B30"
        elif days <= 3:
            priority = "high"
            priority_icon = "🟡"
            priority_color = "#FFFBF5"
            border_color = "#FF9500"
        else:
            priority = "normal"
            priority_icon = "🟢"
            priority_color = "#F0FFF4"
            border_color = "#34C759"

        # 创建卡片框架
        card = ctk.CTkFrame(
            self.patient_list_frame,
            fg_color=priority_color,
            corner_radius=12,
            border_width=2,
            border_color=border_color
        )
        card.pack(fill="x", pady=(0, 10))

        # 添加点击事件
        card.configure(cursor="hand2")
        card.bind("<Button-1>", lambda e, p=patient: self._select_patient(p))

        # 患者头部
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(10, 5))

        # 优先级图标
        icon_label = ctk.CTkLabel(header, text=priority_icon, font=ctk.CTkFont(size=18))
        icon_label.pack(side="left", padx=(0, 8))

        # 患者信息
        info_frame = ctk.CTkFrame(header, fg_color="transparent")
        info_frame.pack(side="left", expand=True, fill="x")

        name_label = ctk.CTkLabel(
            info_frame,
            text=patient.name,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")

        meta_label = ctk.CTkLabel(
            info_frame,
            text=f"第{days}天 | {patient.hospital_number}",
            font=ctk.CTkFont(size=12),
            text_color="#666666",
            anchor="w"
        )
        meta_label.pack(anchor="w")

        # 诊断
        diagnosis_label = ctk.CTkLabel(
            card,
            text=patient.diagnosis or "未填写诊断",
            font=ctk.CTkFont(size=13),
            text_color="#666666",
            anchor="w",
            padx=12
        )
        diagnosis_label.pack(anchor="w", pady=(0, 5))

    def _select_patient(self, patient: Patient):
        """选中患者"""
        self.current_patient = patient

        # 清空工作区
        for widget in self.workspace.winfo_children():
            widget.destroy()

        # 创建患者信息卡片
        self._create_patient_info_card(patient)

        # 创建任务卡片
        self._create_patient_task_card(patient)

        # 创建病程记录卡片
        self._create_note_generation_card(patient)

    def _create_patient_info_card(self, patient: Patient):
        """创建患者信息卡片"""
        days = (date.today() - patient.admission_date).days

        frame = ctk.CTkFrame(self.workspace, fg_color="white", corner_radius=12)

        # 标题
        title = ctk.CTkLabel(
            frame,
            text="患者信息",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))

        # 患者详细信息
        details_frame = ctk.CTkFrame(frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=20, pady=(0, 15))

        # 两列布局
        details = [
            ("住院号：", patient.hospital_number),
            ("姓名：", patient.name or "未填写"),
            ("性别：", patient.gender or "未填写"),
            ("年龄：", f"{patient.age}岁" if patient.age else "未填写"),
            ("入院：", f"{patient.admission_date} (第{days}天)"),
            ("诊断：", patient.diagnosis or "未填写")
        ]

        for i, (label, value) in enumerate(details):
            if i % 2 == 0:
                row_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=(0, 8))

            label_widget = ctk.CTkLabel(
                row_frame,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#666666",
                width=100,
                anchor="w"
            )
            label_widget.pack(side="left")

            value_widget = ctk.CTkLabel(
                row_frame,
                text=value,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            )
            value_widget.pack(side="left", expand=True, fill="x")

        frame.pack(fill="x", pady=(0, 15))

    def _create_patient_task_card(self, patient: Patient):
        """创建患者任务卡片"""
        days = (date.today() - patient.admission_date).days

        frame = ctk.CTkFrame(self.workspace, fg_color="white", corner_radius=12)

        # 标题
        title = ctk.CTkLabel(
            frame,
            text="今日任务",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))

        # 任务列表
        tasks_frame = ctk.CTkFrame(frame, fg_color="transparent")
        tasks_frame.pack(fill="x", padx=20, pady=(0, 15))

        # 根据住院天数生成任务
        tasks = []
        if days >= 85:
            tasks.append(("⚠️", f"住院第{days}天，注意90天限制", "#FFF5F5", "#FF3B30"))
        if days == 2:
            tasks.append(("🔬", "需查看化验结果", "#FFFBF5", "#FF9500"))
        if days % 30 == 0:
            tasks.append(("📋", f"需书写阶段小结（第{days}天）", "#FFFBF5", "#FF9500"))

        if not tasks:
            tasks.append(("✓", "今日无特殊任务", "#F0FFF4", "#34C759"))

        for icon, text, bg_color, border_color in tasks:
            task_frame = ctk.CTkFrame(
                tasks_frame,
                fg_color=bg_color,
                corner_radius=8,
                border_width=1,
                border_color=border_color
            )
            task_frame.pack(fill="x", pady=(0, 8))

            task_label = ctk.CTkLabel(
                task_frame,
                text=f" {icon}  {text}",
                font=ctk.CTkFont(size=13),
                anchor="w",
                padx=12,
                pady=8
            )
            task_label.pack(fill="x")

        frame.pack(fill="x", pady=(0, 15))

    def _create_note_generation_card(self, patient: Patient):
        """创建病程记录生成卡片"""
        frame = ctk.CTkFrame(self.workspace, fg_color="white", corner_radius=12)

        # 标题
        title = ctk.CTkLabel(
            frame,
            text="病程记录生成",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))

        # 工具栏
        toolbar = ctk.CTkFrame(frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=(0, 15))

        btn1 = ctk.CTkButton(
            toolbar,
            text="📋 查看历史",
            width=100,
            height=32,
            fg_color="#F2F2F7",
            hover_color="#E5E5EA",
            text_color="#000000",
            font=ctk.CTkFont(size=12),
            command=lambda: self._show_history(patient)
        )
        btn1.pack(side="left", padx=(0, 8))

        btn2 = ctk.CTkButton(
            toolbar,
            text="🔍 搜索资料",
            width=100,
            height=32,
            fg_color="#F2F2F7",
            hover_color="#E5E5EA",
            text_color="#000000",
            font=ctk.CTkFont(size=12)
        )
        btn2.pack(side="left", padx=(0, 8))

        # 当日情况输入
        label = ctk.CTkLabel(
            frame,
            text="当日情况：",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        label.pack(anchor="w", padx=20, pady=(0, 5))

        self.daily_input = ctk.CTkTextbox(
            frame,
            height=80,
            font=ctk.CTkFont(size=14),
            border_color="#C6C6C8",
            border_width=2
        )
        self.daily_input.pack(fill="x", padx=20, pady=(0, 15))

        self.daily_input.insert("1.0", "请输入患者今日情况，例如：患者右上肢肌力较前改善，可完成抓握动作，继续康复训练...")

        # 操作按钮
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        generate_btn = ctk.CTkButton(
            btn_frame,
            text="✨ AI生成",
            height=38,
            fg_color="#007AFF",
            hover_color="#0051D5",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self._generate_note(patient)
        )
        generate_btn.pack(side="left", expand=True, fill="x", padx=(0, 8))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 保存",
            height=38,
            fg_color="#34C759",
            hover_color="#2DB84D",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self._save_note(patient)
        )
        save_btn.pack(side="left", expand=True, fill="x", padx=(0, 8))

        export_btn = ctk.CTkButton(
            btn_frame,
            text="📄 导出txt",
            height=38,
            fg_color="#F2F2F7",
            hover_color="#E5E5EA",
            text_color="#000000",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self._export_note()
        )
        export_btn.pack(side="left", expand=True, fill="x")

        # 预览区域
        preview_label = ctk.CTkLabel(
            frame,
            text="AI生成预览：",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        preview_label.pack(anchor="w", padx=20, pady=(10, 5))

        self.preview_text = ctk.CTkTextbox(
            frame,
            height=150,
            font=ctk.CTkFont(size=13),
            border_color="#C6C6C8",
            border_width=2
        )
        self.preview_text.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.preview_text.insert("1.0", "AI生成的病程记录将显示在这里，可以直接编辑...")

        frame.pack(fill="both", expand=True)

    # ==================== 交互功能 ====================

    def _show_new_patient_dialog(self):
        """显示新建患者对话框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("新建患者")
        dialog.geometry("500x600")
        dialog.grab_set()  # 模态对话框

        # 表单容器
        form_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 住院号（必填）
        ctk.CTkLabel(form_frame, text="住院号 *", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        hospital_number_entry = ctk.CTkEntry(form_frame, placeholder_text="请输入住院号")
        hospital_number_entry.pack(fill="x", pady=(0, 15))

        # 姓名
        ctk.CTkLabel(form_frame, text="姓名", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        name_entry = ctk.CTkEntry(form_frame, placeholder_text="请输入姓名")
        name_entry.pack(fill="x", pady=(0, 15))

        # 性别
        ctk.CTkLabel(form_frame, text="性别", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        gender_combo = ctk.CTkComboBox(form_frame, values=["男", "女"])
        gender_combo.pack(fill="x", pady=(0, 15))

        # 年龄
        ctk.CTkLabel(form_frame, text="年龄", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        age_entry = ctk.CTkEntry(form_frame, placeholder_text="请输入年龄")
        age_entry.pack(fill="x", pady=(0, 15))

        # 入院日期
        ctk.CTkLabel(form_frame, text="入院日期", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        admission_entry = ctk.CTkEntry(form_frame, placeholder_text="YYYY-MM-DD")
        admission_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        admission_entry.pack(fill="x", pady=(0, 15))

        # 诊断
        ctk.CTkLabel(form_frame, text="诊断", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        diagnosis_entry = ctk.CTkEntry(form_frame, placeholder_text="请输入诊断")
        diagnosis_entry.pack(fill="x", pady=(0, 15))

        # 按钮
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        def save_patient():
            hospital_number = hospital_number_entry.get().strip()
            if not hospital_number:
                messagebox.showerror("错误", "住院号不能为空！")
                return

            # 检查是否已存在
            existing = self.db_manager.get_patient_by_hospital_number(hospital_number)
            if existing:
                messagebox.showerror("错误", f"住院号 {hospital_number} 已存在！")
                return

            # 创建患者数据
            patient_data = {
                "hospital_number": hospital_number,
                "name": name_entry.get().strip() or None,
                "gender": gender_combo.get() or None,
                "age": int(age_entry.get()) if age_entry.get().strip() else None,
                "admission_date": datetime.strptime(admission_entry.get(), "%Y-%m-%d").date(),
                "diagnosis": diagnosis_entry.get().strip() or None
            }

            # 保存到数据库
            try:
                self.db_manager.add_patient(patient_data)
                messagebox.showinfo("成功", f"患者 {patient_data['name']} 添加成功！")
                dialog.destroy()
                self._load_patients()  # 刷新列表
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="取消",
            height=40,
            fg_color="#F2F2F7",
            hover_color="#E5E5EA",
            text_color="#000000",
            command=dialog.destroy
        )
        cancel_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="保存",
            height=40,
            fg_color="#007AFF",
            hover_color="#0051D5",
            text_color="white",
            command=save_patient
        )
        save_btn.pack(side="left", expand=True, fill="x")

    def _generate_note(self, patient: Patient):
        """AI生成病程记录"""
        if not self.ai_manager:
            messagebox.showwarning("提示", "AI服务未配置，无法生成病程记录。\n请在config.json中配置AI服务的API密钥。")
            return

        daily_input = self.daily_input.get("1.0", "end").strip()

        if not daily_input or daily_input == "请输入患者今日情况，例如：患者右上肢肌力较前改善，可完成抓握动作，继续康复训练...":
            messagebox.showwarning("提示", "请先输入当日情况！")
            return

        # 显示加载提示
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", "正在生成病程记录，请稍候...")

        # 获取历史病程记录
        history_notes = self.db_manager.get_patient_notes(patient.id, limit=5)

        # 构建上下文
        context = {
            "patient_name": patient.name,
            "diagnosis": patient.diagnosis,
            "admission_date": patient.admission_date.strftime("%Y-%m-%d"),
            "daily_condition": daily_input,
            "history_notes": [note.generated_content for note in history_notes if note.generated_content]
        }

        try:
            # 调用AI服务生成
            ai_service = self.ai_manager.get_service()
            if ai_service:
                generated = ai_service.generate_progress_note(context)

                # 显示生成的病程记录
                self.preview_text.delete("1.0", "end")
                self.preview_text.insert("1.0", generated)
            else:
                self.preview_text.delete("1.0", "end")
                self.preview_text.insert("1.0", "错误：未找到可用的AI服务。请检查config.json配置。")

        except Exception as e:
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", f"生成失败：{str(e)}")

    def _save_note(self, patient: Patient):
        """保存病程记录"""
        generated_content = self.preview_text.get("1.0", "end").strip()
        daily_condition = self.daily_input.get("1.0", "end").strip()

        if not generated_content or generated_content == "AI生成的病程记录将显示在这里，可以直接编辑...":
            messagebox.showwarning("提示", "没有可保存的内容！")
            return

        # 计算住院天数
        days = (date.today() - patient.admission_date).days

        note_data = {
            "patient_id": patient.id,
            "hospital_number": patient.hospital_number,
            "record_date": date.today(),
            "day_number": days,
            "record_type": "住院医师查房",
            "daily_condition": daily_condition,
            "generated_content": generated_content,
            "is_edited": False
        }

        try:
            self.db_manager.add_progress_note(note_data)
            messagebox.showinfo("成功", "病程记录保存成功！")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")

    def _export_note(self):
        """导出病程记录为txt"""
        content = self.preview_text.get("1.0", "end").strip()

        if not content:
            messagebox.showwarning("提示", "没有可导出的内容！")
            return

        # 选择保存位置
        file_path = filedialog.asksaveasfilename(
            title="导出病程记录",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"导出成功！\n保存位置：{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败：{str(e)}")

    def _show_history(self, patient: Patient):
        """显示历史病程记录"""
        history_notes = self.db_manager.get_patient_notes(patient.id, limit=10)

        if not history_notes:
            messagebox.showinfo("历史记录", "暂无历史病程记录")
            return

        # 创建历史记录窗口
        history_window = ctk.CTkToplevel(self)
        history_window.title(f"历史病程记录 - {patient.name}")
        history_window.geometry("700x500")

        # 添加滚动文本框
        text_widget = ctk.CTkTextbox(history_window, font=ctk.CTkFont(size=12))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        # 显示历史记录
        content = ""
        for note in reversed(history_notes):
            content += f"{'='*60}\n"
            content += f"日期：{note.record_date}  第{note.day_number}天  {note.record_type}\n"
            content += f"{'='*60}\n\n"
            if note.daily_condition:
                content += f"【当日情况】\n{note.daily_condition}\n\n"
            content += f"【病程记录】\n{note.generated_content}\n\n"

        text_widget.insert("1.0", content)
        text_widget.configure(state="disabled")  # 只读

    def _insert_phrase(self, phrase: str):
        """插入常用短语"""
        if hasattr(self, 'daily_input'):
            current_text = self.daily_input.get("1.0", "end")
            self.daily_input.delete("1.0", "end")
            self.daily_input.insert("1.0", current_text + phrase)

    def _on_diagnosis_selected(self, choice):
        """诊断模板选择回调"""
        if hasattr(self, 'daily_input') and choice != "选择诊断...":
            current_text = self.daily_input.get("1.0", "end")
            self.daily_input.delete("1.0", "end")
            self.daily_input.insert("1.0", f"{current_text}\n诊断：{choice}")

    def _on_treatment_selected(self, choice):
        """处理意见模板选择回调"""
        if hasattr(self, 'preview_text') and choice != "选择处理...":
            current_text = self.preview_text.get("1.0", "end")
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", f"{current_text}\n处理：{choice}")

    def _show_reminders(self):
        """显示今日提醒"""
        reminders = self.db_manager.get_today_reminders()

        if not reminders:
            messagebox.showinfo("今日提醒", "暂无待完成提醒")
            return

        # 创建提醒窗口
        reminder_window = ctk.CTkToplevel(self)
        reminder_window.title("今日提醒")
        reminder_window.geometry("600x400")

        # 添加列表
        frame = ctk.CTkScrollableFrame(reminder_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        for reminder in reminders:
            item = ctk.CTkFrame(frame, corner_radius=8)
            item.pack(fill="x", pady=5)

            # 根据优先级设置颜色
            if reminder.priority == "紧急":
                bg_color = "#FFF5F5"
                border_color = "#FF3B30"
            elif reminder.priority == "高":
                bg_color = "#FFFBF5"
                border_color = "#FF9500"
            else:
                bg_color = "#F0FFF4"
                border_color = "#34C759"

            item.configure(fg_color=bg_color, border_width=1, border_color=border_color)

            # 描述
            desc = ctk.CTkLabel(
                item,
                text=f"{reminder.reminder_type}: {reminder.description}",
                anchor="w",
                padx=15,
                pady=10
            )
            desc.pack(fill="x")


if __name__ == "__main__":
    app = ImprovedMainWindow()
    app.mainloop()
