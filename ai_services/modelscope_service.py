"""
魔搭AI服务实现 - 使用OpenAI兼容接口
"""
from openai import OpenAI
from ai_services.base_service import AIService


class ModelScopeService(AIService):
    """魔搭AI服务"""

    def __init__(self, api_key: str, model: str = "deepseek-ai/DeepSeek-V3.2", base_url: str = "https://api-inference.modelscope.cn/v1"):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            model=model
        )
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

    def _call_api(self, messages: list, temperature: float = 0.7, enable_thinking: bool = False) -> str:
        """调用魔搭API"""
        try:
            # 构建extra_body参数（DeepSeek V3.2支持thinking模式）
            extra_body = {}
            if "V3.2" in self.model:
                extra_body["enable_thinking"] = enable_thinking

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                extra_body=extra_body if extra_body else None
            )

            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"魔搭API调用失败: {str(e)}")

    def extract_patient_info(self, initial_note: str) -> dict:
        """从首次病程记录提取患者信息"""
        prompt = f"""你是一位专业的病历录入助手。请从以下首次病程记录中提取结构化信息，以JSON格式返回：

首次病程记录：
{initial_note}

需要提取的字段：
- 姓名
- 性别
- 年龄
- 入院日期（格式：YYYY-MM-DD）
- 主诉
- 诊断
- 既往史（如有）
- 过敏史（如有）

请只返回JSON，不要其他内容。"""

        messages = [
            {"role": "system", "content": "你是专业的医疗信息提取助手。"},
            {"role": "user", "content": prompt}
        ]

        response = self._call_api(messages, temperature=0.3)
        # TODO: 添加JSON解析和错误处理
        return response

    def generate_progress_note(self, context: dict) -> str:
        """生成病程记录"""
        # 获取医生信息
        doctor_info = context.get('doctor_info', {}) or {}
        record_type = context.get('record_type', '住院医师查房')

        # 根据记录类型生成签名（参照 rounds_generator.py 的格式）
        signature_lines = []

        if record_type == '住院医师查房':
            # 住院医师查房：只有住院医师签名
            resident = doctor_info.get('resident', '')
            if resident:
                signature_lines.append(f"住院医师：{resident}")
            else:
                signature_lines.append("住院医师：")

        elif record_type == '主治医师查房':
            # 主治医师查房：住院医师 + 主治医师签名
            resident = doctor_info.get('resident', '')
            attending = doctor_info.get('attending', '')
            if resident:
                signature_lines.append(f"住院医师：{resident}")
            else:
                signature_lines.append("住院医师：")
            if attending:
                signature_lines.append(f"主治医师：{attending}")
            else:
                signature_lines.append("主治医师：")

        elif record_type == '主任医师查房':
            # 主任医师查房：住院医师 + 主任医师签名
            resident = doctor_info.get('resident', '')
            chief = doctor_info.get('chief', '')
            if resident:
                signature_lines.append(f"住院医师：{resident}")
            else:
                signature_lines.append("住院医师：")
            if chief:
                signature_lines.append(f"主任医师：{chief}")
            else:
                signature_lines.append("主任医师：")

        else:
            # 阶段小结等其他类型
            signature_lines.append("医师签名：")

        signature = '\n'.join(signature_lines)

        prompt = f"""你是一位中医院康复科的专业医师。请根据以下信息生成今日病程记录：

【患者基本信息】
姓名：{context['name']}
性别：{context['gender']}
年龄：{context['age']}
诊断：{context['diagnosis']}
住院第{context['day_number']}天

【首次病程记录】
{context['initial_note']}

【最近2次病程记录】
{context.get('recent_notes_1', '无')}
{context.get('recent_notes_2', '无')}

【今日情况】
{context['daily_condition']}

【记录类型】
{context['record_type']}

要求：
1. 语言风格符合中医病历规范
2. 根据记录类型调整内容详略（住院医师详细，主治/主任医师简洁）
3. 主诉部分结合今日情况更新
4. 查体部分按实际情况描述，如无特殊变化可写"查体同前"
5. 分析和处理意见要体现中医特色和康复专业特点
6. 字数控制在200-400字
7. **重要：不需要输出签名，签名会自动添加**

请直接输出病程记录内容（不要包含签名），格式如下：
YYYY-MM-DD HH:MM {context['record_type']}
主诉：...
查体：...
分析：...
处理：..."""

        messages = [
            {"role": "system", "content": "你是中医院康复科的专业医师。"},
            {"role": "user", "content": prompt}
        ]

        # 调用AI生成内容（不含签名）
        content = self._call_api(messages, temperature=0.7)

        # 直接追加签名（不通过AI）
        content_with_signature = f"{content}\n{signature}"

        return content_with_signature

    def generate_rehab_plan(self, context: dict) -> dict:
        """生成康复计划"""
        patient_info = context.get('patient_info', {})

        prompt = f"""请为以下患者制定详细的康复计划：

【患者基本信息】
姓名：{patient_info.get('name', '未提供')}
性别：{patient_info.get('gender', '未提供')}
年龄：{patient_info.get('age', '未提供')}
诊断：{patient_info.get('diagnosis', '未提供')}
主诉：{patient_info.get('chief_complaint', '未提供')}
专科检查：{patient_info.get('specialist_exam', '未提供')}

【首次病程记录】
{context.get('initial_note', '未提供')}

【参考资料】
{context.get('knowledge_base', '无')}

请生成包括以下内容的康复计划，以JSON格式返回：

{{
    "short_term_goals": "短期目标（1-2周）：具体可衡量的康复目标",
    "long_term_goals": "长期目标（1-3个月）：整体康复目标",
    "training_plan": [
        {{
            "name": "训练项目名称",
            "frequency": "每日/每周X次",
            "duration": "每次X分钟",
            "sets": "X组",
            "intensity": "强度描述",
            "notes": "注意事项"
        }}
    ]
}}

要求：
1. 目标要具体、可衡量、可达成
2. 训练计划要符合康复医学规范
3. 结合患者具体诊断制定针对性方案
4. 至少包含3-5个训练项目

请只返回JSON，不要其他内容。"""

        messages = [
            {"role": "system", "content": "你是专业的康复治疗师，精通中医康复和现代康复医学。"},
            {"role": "user", "content": prompt}
        ]

        response = self._call_api(messages, temperature=0.7)

        # 尝试解析JSON响应
        try:
            import json
            # 如果AI返回的是纯文本JSON，直接解析
            plan_data = json.loads(response)

            # 转换training_plan为JSON字符串
            if isinstance(plan_data.get('training_plan'), list):
                plan_data['training_plan'] = json.dumps(plan_data['training_plan'], ensure_ascii=False)

            return plan_data
        except json.JSONDecodeError:
            # 如果解析失败，返回默认格式
            return {
                "short_term_goals": "短期目标：改善患者功能状态，提高日常生活活动能力",
                "long_term_goals": "长期目标：最大限度恢复患者功能，回归家庭和社会",
                "training_plan": json.dumps([
                    {
                        "name": "关节活动度训练",
                        "frequency": "每日2次",
                        "duration": "20分钟",
                        "sets": "3组",
                        "intensity": "中等强度",
                        "notes": "在无痛范围内进行"
                    },
                    {
                        "name": "肌力训练",
                        "frequency": "每日1次",
                        "duration": "30分钟",
                        "sets": "3-4组",
                        "intensity": "渐进抗阻",
                        "notes": "根据患者耐受情况调整"
                    },
                    {
                        "name": "平衡训练",
                        "frequency": "每日1次",
                        "duration": "15分钟",
                        "sets": "2-3组",
                        "intensity": "中等强度",
                        "notes": "注意保护，防止跌倒"
                    }
                ], ensure_ascii=False)
            }

    def extract_common_phrases(self, content: str, preprocessed: bool = False) -> list:
        """
        从病程记录文件中提取常用语句并分类

        Args:
            content: 文本内容（原始文档或预处理后的语句列表）
            preprocessed: 是否已预处理（如果为True，AI只做优化和分类）
        """
        if preprocessed:
            # 预处理模式：AI只负责优化语句并分类
            prompt = f"""你是一位专业的医疗文书编辑助手。请对以下从病程记录中提取的语句进行优化和分类。

【已提取的语句列表】
{content}

请对每条语句进行以下处理：
1. 语句优化：使语句更规范、通顺、符合医疗文书标准
2. 去除语句中的具体信息（如人名、具体日期、床号等）
3. 语句归类：将语句分到合适的类别中

类别包括：
1. 症状描述类：描述患者症状、表现的语句
2. 检查结果类：描述各类检查结果的语句
3. 治疗方案类：描述治疗措施的语句
4. 康复训练类：描述康复训练项目的语句
5. 护理事项类：描述护理注意事项的语句
6. 病情变化类：描述病情变化的语句
7. 用药记录类：描述用药情况的语句

要求：
1. 优化后的语句要简洁、通用、可复用
2. 保持原意，但使表达更专业
3. 如果语句过短或无意义，可以不处理
4. 请处理所有语句

请以JSON格式返回，格式如下：
[
    {{
        "content": "优化后的语句内容",
        "category": "类别名称"
    }}
]

请只返回JSON数组，不要其他内容。"""
        else:
            # 原始模式：AI负责提取和分类（保留用于小文档）
            prompt = f"""你是一位专业的医疗文本分析助手。请从以下病程记录内容中提取常用的、可复用的语句，并进行分类。

【病程记录内容】
{content}

请分析这些病程记录，提取出：
1. 症状描述类：描述患者症状、表现的语句
2. 检查结果类：描述各类检查结果的语句
3. 治疗方案类：描述治疗措施的语句
4. 康复训练类：描述康复训练项目的语句
5. 护理事项类：描述护理注意事项的语句
6. 病情变化类：描述病情变化的语句
7. 用药记录类：描述用药情况的语句

要求：
1. 提取的语句要简洁、通用、可复用
2. 每个类别提取3-5条最常用的语句
3. 语句要完整，符合医疗文书规范
4. 避免提取过于具体的人名、日期等信息

请以JSON格式返回，格式如下：
[
    {{
        "content": "语句内容",
        "category": "类别名称"
    }}
]

请只返回JSON数组，不要其他内容。"""

        messages = [
            {"role": "system", "content": "你是专业的医疗文本分析助手，擅长优化和分类医疗语句。"},
            {"role": "user", "content": prompt}
        ]

        response = self._call_api(messages, temperature=0.5)

        # 尝试解析JSON响应
        try:
            import json
            phrases = json.loads(response)

            # 验证返回格式
            if isinstance(phrases, list):
                # 确保每个元素都有content和category字段
                validated_phrases = []
                for phrase in phrases:
                    if isinstance(phrase, dict) and 'content' in phrase and 'category' in phrase:
                        validated_phrases.append({
                            'content': phrase['content'],
                            'category': phrase['category']
                        })
                return validated_phrases
            else:
                return []
        except json.JSONDecodeError:
            # 如果解析失败，返回空列表
            print(f"AI返回的内容无法解析为JSON: {response}")
            return []

