"""
硅基流动嵌入服务
"""
import requests
from typing import list


class SiliconFlowEmbedder:
    """硅基流动嵌入服务"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.siliconflow.cn/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def encode(self, texts: list[str]) -> list[list[float]]:
        """将文本向量化

        Args:
            texts: 文本列表

        Returns:
            向量列表（每个向量1024维）
        """
        try:
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers=self.headers,
                json={
                    "model": "BAAI/bge-large-zh-v1.5",
                    "input": texts,
                    "encoding_format": "float"
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            # 提取向量
            embeddings = [item["embedding"] for item in result["data"]]
            return embeddings

        except Exception as e:
            raise Exception(f"硅基流动API调用失败: {str(e)}")
