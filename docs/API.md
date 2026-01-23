# 康复科助手 - API文档

## 数据库模块 (database)

### DBManager

数据库管理器，提供所有数据库操作接口。

#### 方法

**add_patient(patient_data: dict) -> int**
- 添加患者，返回患者ID
- 参数：患者数据字典
- 返回：患者ID

**get_patient_by_hospital_number(hospital_number: str) -> Patient**
- 根据住院号获取患者
- 参数：住院号
- 返回：患者对象或None

**get_all_patients(include_discharged: bool = False) -> list[Patient]**
- 获取所有患者
- 参数：是否包含已出院患者
- 返回：患者列表

**add_progress_note(note_data: dict) -> int**
- 添加病程记录
- 参数：病程记录数据
- 返回：记录ID

**get_patient_notes(patient_id: int, limit: int = 5) -> list[ProgressNote]**
- 获取患者最近的病程记录
- 参数：患者ID，限制数量
- 返回：病程记录列表

**add_reminder(reminder_data: dict) -> int**
- 添加提醒
- 参数：提醒数据
- 返回：提醒ID

**get_today_reminders(priority_filter: str = None) -> list[Reminder]**
- 获取今日待完成提醒
- 参数：优先级过滤
- 返回：提醒列表

## AI服务模块 (ai_services)

### AIServiceManager

AI服务管理器，统一管理多个AI服务商。

#### 方法

**get_service(provider: str = None) -> AIService**
- 获取AI服务实例
- 参数：服务商名称（modelscope/deepseek/kimi）
- 返回：AI服务对象

**get_embedder() -> SiliconFlowEmbedder**
- 获取嵌入服务
- 返回：嵌入服务对象

### AIService

AI服务抽象基类，所有服务商实现此接口。

#### 方法

**extract_patient_info(initial_note: str) -> dict**
- 从首次病程记录提取患者信息
- 参数：首次病程记录文本
- 返回：患者信息字典

**generate_progress_note(context: dict) -> str**
- 生成病程记录
- 参数：上下文信息（患者信息、今日情况等）
- 返回：生成的病程记录文本

**generate_rehab_plan(patient_info: dict) -> dict**
- 生成康复计划
- 参数：患者信息
- 返回：康复计划

## 知识库模块 (knowledge_base)

### KnowledgeBaseManager

知识库管理器，基于ChromaDB实现语义检索。

#### 方法

**add_document(file_path: str) -> dict**
- 添加文档并向量化
- 参数：文件路径
- 返回：处理结果统计

**search(query: str, top_k: int = 5) -> list[dict]**
- 语义检索
- 参数：查询文本，返回结果数量
- 返回：检索结果列表

**get_stats() -> dict**
- 获取知识库统计信息
- 返回：统计信息

## 业务模块 (modules)

### PatientManager

患者管理器。

#### 方法

**create_patient(hospital_number: str, initial_note: str) -> dict**
- 创建新患者
- 参数：住院号，首次病程记录
- 返回：创建结果

### ProgressNoteGenerator

病程记录生成器。

#### 方法

**generate_note(hospital_number: str, daily_condition: str, record_type: str) -> dict**
- 生成病程记录
- 参数：住院号，当日情况，记录类型
- 返回：生成结果

### ReminderSystem

提醒系统。

#### 方法

**get_today_reminders() -> list[dict]**
- 获取今日所有待完成提醒
- 返回：提醒列表

**mark_completed(reminder_id: int) -> bool**
- 标记提醒为已完成
- 参数：提醒ID
- 返回：是否成功

## 数据模型

### Patient
- id: 患者ID
- hospital_number: 住院号
- name: 姓名
- gender: 性别
- age: 年龄
- admission_date: 入院日期
- diagnosis: 诊断
- initial_note: 首次病程记录

### ProgressNote
- id: 记录ID
- patient_id: 患者ID
- hospital_number: 住院号
- record_date: 记录日期
- day_number: 住院天数
- record_type: 记录类型
- daily_condition: 当日情况
- generated_content: 生成内容

### Reminder
- id: 提醒ID
- patient_id: 患者ID
- reminder_type: 提醒类型
- reminder_date: 提醒日期
- description: 描述
- priority: 优先级（紧急/高/中/低）
- is_completed: 是否完成
