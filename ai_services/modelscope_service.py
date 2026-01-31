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
        prompt = f"""你是一位专业的病历录入助手。请从以下首次病程记录中提取结构化信息，以JSON格式返回。

首次病程记录：
{initial_note}

**重要要求：**
1. 必须返回严格的JSON格式，不要包含其他文字说明
2. 需要提取的字段如下：
   - name: 姓名
   - gender: 性别（男/女）
   - age: 年龄（数字）
   - admission_date: 入院日期（格式：YYYY-MM-DD）
   - chief_complaint: 主诉
   - diagnosis: 诊断（包括中医和西医诊断）
   - past_history: 既往史（从病程记录中仔细查找，包括既往疾病史、手术史、外伤史等）
   - allergy_history: 过敏史（如果没有明确说明，填"无"或"未提及"）
   - specialist_exam: 专科查体（包括完整的体格检查内容，如生命体征、神志、瞳孔、肌力、肌张力等详细查体记录）

3. 请返回如下格式的JSON：
{{
    "name": "患者姓名",
    "gender": "性别",
    "age": 年龄数字,
    "admission_date": "YYYY-MM-DD",
    "chief_complaint": "主诉内容",
    "diagnosis": "诊断内容",
    "past_history": "既往史内容（注意：从病程中仔细提取，包括高血压、糖尿病、手术史等）",
    "allergy_history": "过敏史内容（如未提及，填'无'）",
    "specialist_exam": "专科查体完整内容（包括体温、脉搏、血压、神志、查体发现等所有体格检查信息）"
}}

4. **特别注意**：请仔细阅读整个病程记录，不要遗漏任何字段。如果某个字段确实没有相关信息，填"未提及"或"无"。

请只返回JSON，不要其他内容。"""

        messages = [
            {"role": "system", "content": "你是专业的医疗信息提取助手，擅长从病历中提取结构化数据。"},
            {"role": "user", "content": prompt}
        ]

        try:
            import json
            import re

            response = self._call_api(messages, temperature=0.3)

            # 打印原始响应用于调试
            print(f"[DEBUG] AI原始响应:")
            print(response)
            print(f"[DEBUG] 响应长度: {len(response)} 字符")

            # 清理响应中的markdown代码块标记
            cleaned_response = response.strip()
            cleaned_response = re.sub(r'^```json\s*', '', cleaned_response, flags=re.DOTALL)
            cleaned_response = re.sub(r'^```\s*', '', cleaned_response, flags=re.DOTALL)
            cleaned_response = re.sub(r'\s*```\s*$', '', cleaned_response, flags=re.DOTALL)

            print(f"[DEBUG] 清理后的响应:")
            print(cleaned_response)

            # 解析JSON
            patient_data = json.loads(cleaned_response)

            print(f"[DEBUG] 解析后的患者数据:")
            print(json.dumps(patient_data, ensure_ascii=False, indent=2))

            # 验证必需字段
            required_fields = ['name', 'gender', 'age', 'admission_date']
            missing_fields = [field for field in required_fields if not patient_data.get(field)]

            if missing_fields:
                print(f"[ERROR] 缺少必需字段: {missing_fields}")
                print(f"[ERROR] 当前字段: {list(patient_data.keys())}")
                raise Exception(f"缺少必需字段: {', '.join(missing_fields)}")

            # 为可选字段提供默认值
            optional_fields = {
                'past_history': patient_data.get('past_history') or '',
                'allergy_history': patient_data.get('allergy_history') or '无',
                'specialist_exam': patient_data.get('specialist_exam') or '',
                'chief_complaint': patient_data.get('chief_complaint') or '',
                'diagnosis': patient_data.get('diagnosis') or ''
            }

            # 合并数据
            patient_data.update(optional_fields)

            print(f"[DEBUG] 最终患者数据（包含默认值）:")
            print(json.dumps(patient_data, ensure_ascii=False, indent=2))

            return patient_data

        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON解析失败: {str(e)}")
            print(f"[ERROR] 原始响应: {response}")
            raise Exception(f"AI返回的内容无法解析为JSON: {str(e)}\n原始响应: {response}")
        except Exception as e:
            print(f"[ERROR] 提取患者信息异常: {str(e)}")
            raise Exception(f"提取患者信息失败: {str(e)}")

    def generate_progress_note(self, context: dict) -> str:
        """生成病程记录"""
        # 获取医生信息
        doctor_info = context.get('doctor_info', {}) or {}
        record_type = context.get('record_type', '住院医师查房')

        # 根据记录类型确定标题中的医生姓名
        doctor_name_in_title = ''
        if record_type == '住院医师查房':
            doctor_name_in_title = doctor_info.get('resident', '')
        elif record_type == '主治医师查房':
            doctor_name_in_title = doctor_info.get('attending', '')
        elif record_type == '主任医师查房':
            doctor_name_in_title = doctor_info.get('chief', '')

        # 构建标题（包含医生姓名）
        title_doctor_part = f" {doctor_name_in_title}" if doctor_name_in_title else ""

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
4. **查体部分：必须保留今日情况中的查体内容，包括"腹软无压痛。"后面的专科检查信息，不要简化为"查体同前"**
5. 分析和处理意见要体现中医特色和康复专业特点
6. 字数控制在200-400字
7. **重要：不需要输出签名，签名会自动添加**

请直接输出病程记录内容（不要包含签名），格式如下：
YYYY-MM-DD HH:MM{title_doctor_part} {context['record_type']}
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

**重要：必须使用以下分类体系，不要创建新的类别：**

**1. 基础评估与诊断**
- 症状采集（主诉、现病史、既往史）
- 体格检查（肌力、肌张力、关节活动度、平衡功能）
- 辅助检查（影像学、实验室检查、电生理检查）
- 诊断结论（中医诊断、西医诊断）

**2. 治疗方案制定**
- 中医特色治疗（针刺治疗、电针参数、方义解析）
- 中药治疗（方剂名称、药物组成、剂量、煎服法）
- 西药治疗（药物名称、剂量、给药途径、治疗目的）
- 康复治疗（运动功能训练、训练方法、强度）
- 护理操作（分级护理、特殊操作如导尿/吸痰）

**3. 管理与监测**
- 医嘱与护理（饮食类别、护理级别、体位要求）
- 风险防控（跌倒/压疮/误吸/血栓预防措施）
- 病情监测（生命体征记录、血糖/血压监测、症状变化）
- 并发症处理（感染、痉挛、肩手综合征的管理）

**4. 医患沟通与记录**
- 医患沟通（知情同意、康复预期、费用说明）
- 健康宣教（家庭训练指导、生活方式指导、用药教育）

要求：
1. 优化后的语句要简洁、通用、可复用
2. 保持原意，但使表达更专业
3. 如果语句过短或无意义，可以不处理
4. 请处理所有语句
5. **每个语句必须归入上述4个大类下的具体二级分类中，category字段格式为："大类名称-二级分类"，例如："基础评估与诊断-症状采集"**

请以JSON格式返回，格式如下：
[
    {{
        "content": "优化后的语句内容",
        "category": "大类名称-二级分类名称"
    }}
]

请只返回JSON数组，不要其他内容。"""
        else:
            # 原始模式：AI负责提取和分类（保留用于小文档）
            prompt = f"""你是一位专业的医疗文本分析助手。请从以下病程记录内容中提取常用的、可复用的语句，并进行分类。

【病程记录内容】
{content}

请分析这些病程记录，按照以下分类体系提取语句：

**1. 基础评估与诊断**
- 症状采集（主诉、现病史、既往史）
- 体格检查（肌力、肌张力、关节活动度、平衡功能）
- 辅助检查（影像学、实验室检查、电生理检查）
- 诊断结论（中医诊断、西医诊断）

**2. 治疗方案制定**
- 中医特色治疗（针刺治疗、电针参数、方义解析）
- 中药治疗（方剂名称、药物组成、剂量、煎服法）
- 西药治疗（药物名称、剂量、给药途径、治疗目的）
- 康复治疗（运动功能训练、训练方法、强度）
- 护理操作（分级护理、特殊操作如导尿/吸痰）

**3. 管理与监测**
- 医嘱与护理（饮食类别、护理级别、体位要求）
- 风险防控（跌倒/压疮/误吸/血栓预防措施）
- 病情监测（生命体征记录、血糖/血压监测、症状变化）
- 并发症处理（感染、痉挛、肩手综合征的管理）

**4. 医患沟通与记录**
- 医患沟通（知情同意、康复预期、费用说明）
- 健康宣教（家庭训练指导、生活方式指导、用药教育）

要求：
1. 提取的语句要简洁、通用、可复用
2. 每个二级分类提取3-5条最常用的语句
3. 语句要完整，符合医疗文书规范
4. 避免提取过于具体的人名、日期等信息
5. **category字段格式为："大类名称-二级分类名称"，例如："基础评估与诊断-症状采集"**

请以JSON格式返回，格式如下：
[
    {{
        "content": "语句内容",
        "category": "大类名称-二级分类名称"
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
            import re

            # 清理响应内容：移除可能的Markdown代码块标记
            cleaned_response = response.strip()

            # 移除 ```json 和 ``` 标记
            cleaned_response = re.sub(r'^```json\s*', '', cleaned_response, flags=re.DOTALL)
            cleaned_response = re.sub(r'^```\s*', '', cleaned_response, flags=re.DOTALL)
            cleaned_response = re.sub(r'\s*```$', '', cleaned_response, flags=re.DOTALL)

            # 尝试解析清理后的JSON
            phrases = json.loads(cleaned_response)

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
        except json.JSONDecodeError as e:
            # 如果解析失败，打印详细错误信息
            print(f"AI返回的内容无法解析为JSON")
            print(f"错误信息: {str(e)}")
            print(f"原始响应: {response[:500]}...")  # 只打印前500字符
            return []
        except Exception as e:
            print(f"解析过程中发生错误: {str(e)}")
            print(f"原始响应: {response[:500]}...")
            return []

