"""
文本预处理工具 - 从病程记录中提取高频语句
"""
import re
from difflib import SequenceMatcher
from collections import Counter
from typing import List


def preprocess_medical_records(content: str, max_phrases: int = 80) -> List[str]:
    """
    预处理病程记录，提取高频语句

    Args:
        content: 原始文本内容
        max_phrases: 最多返回多少条语句

    Returns:
        高频语句列表
    """

    # 1. 分句：按句号、换行符、分号分割
    sentences = re.split(r'[。\n；;！!？?]', content)

    # 2. 清洗：去除空白、过短语句、纯数字
    cleaned_sentences = []
    for sent in sentences:
        sent = sent.strip()
        # 过滤条件：
        # - 至少5个字符
        # - 不全是数字
        # - 不全是标点符号
        # - 排除明显的时间日期格式
        if len(sent) >= 5 and not sent.isdigit() and re.search(r'[\u4e00-\u9fa5a-zA-Z]', sent):
            # 排除纯时间日期
            if not re.match(r'^\d{4}[-/年]\d{1,2}[-/月]\d{1,2}', sent):
                cleaned_sentences.append(sent)

    # 3. 去重合并相似句
    unique_sentences = []
    for sent in cleaned_sentences:
        is_duplicate = False
        for existing in unique_sentences:
            similarity = SequenceMatcher(None, sent, existing).ratio()
            if similarity > 0.85:  # 相似度阈值85%
                is_duplicate = True
                break
        if not is_duplicate:
            unique_sentences.append(sent)

    # 4. 统计频次
    # 在原文中查找每条语句出现的次数
    sentence_counts = Counter()
    for sent in unique_sentences:
        # 使用模糊匹配计数
        count = 0
        for original in cleaned_sentences:
            if SequenceMatcher(None, sent, original).ratio() > 0.85:
                count += 1
        sentence_counts[sent] = count

    # 5. 返回高频语句
    top_sentences = sentence_counts.most_common(max_phrases)
    return [sent for sent, count in top_sentences]


def optimize_phrases_for_ai(phrases: List[str], max_content_length: int = 8000) -> str:
    """
    将语句列表格式化为适合AI处理的文本

    Args:
        phrases: 语句列表
        max_content_length: 最大内容长度（避免token超限）

    Returns:
        格式化后的文本
    """
    formatted_lines = []
    current_length = 0

    for i, phrase in enumerate(phrases, 1):
        line = f"{i}. {phrase}"
        if current_length + len(line) > max_content_length:
            break
        formatted_lines.append(line)
        current_length += len(line)

    return "\n".join(formatted_lines)
