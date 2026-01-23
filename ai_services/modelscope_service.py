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

请直接输出病程记录内容，格式如下：
YYYY-MM-DD HH:MM 记录类型
主诉：...
查体：...
分析：...
处理：...
签名：..."""

        messages = [
            {"role": "system", "content": "你是中医院康复科的专业医师。"},
            {"role": "user", "content": prompt}
        ]

        return self._call_api(messages, temperature=0.7)

    def generate_rehab_plan(self, patient_info: dict) -> dict:
        """生成康复计划"""
        prompt = f"""请为以下患者制定康复计划：

患者信息：
姓名：{patient_info['name']}
诊断：{patient_info['diagnosis']}
功能障碍：{patient_info.get('dysfunction', '未详细描述')}

请生成包括以下内容的康复计划：
1. 康复目标（短期和长期）
2. 干预措施（运动疗法、作业治疗、物理因子治疗等）
3. 注意事项

以JSON格式返回。"""

        messages = [
            {"role": "system", "content": "你是专业的康复治疗师。"},
            {"role": "user", "content": prompt}
        ]

        response = self._call_api(messages, temperature=0.7)
        # TODO: 添加JSON解析
        return {"plan": response}
