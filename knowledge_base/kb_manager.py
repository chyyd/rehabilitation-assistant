"""
知识库管理器 - 使用ChromaDB和硅基流动API
"""
import chromadb
from pathlib import Path
import os
from knowledge_base.document_parser import DocumentParser


class KnowledgeBaseManager:
    """知识库管理器"""

    def __init__(self, config: dict, embedder):
        """初始化知识库管理器

        Args:
            config: 知识库配置
            embedder: 硅基流动嵌入服务实例
        """
        self.embedder = embedder
        self.parser = DocumentParser()
        self.chunk_size = config.get("chunk_size", 800)
        self.chunk_overlap = config.get("chunk_overlap", 100)

        # 初始化ChromaDB
        chroma_path = config.get("chroma_path", "./knowledge_base/data")
        Path(chroma_path).mkdir(parents=True, exist_ok=True)

        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="medical_knowledge"
        )

    def add_document(self, file_path: str) -> dict:
        """添加文档并向量化

        Args:
            file_path: 文件路径

        Returns:
            处理结果统计
        """
        try:
            filename = os.path.basename(file_path)

            # 1. 解析文件为文本
            text = self.parser.parse(file_path)
            text_length = len(text)

            # 2. 文本分块
            chunks = self._split_text(text)
            chunk_count = len(chunks)

            # 3. 调用硅基流动API向量化
            embeddings = self.embedder.encode(chunks)
            vector_dim = len(embeddings[0]) if embeddings else 0

            # 4. 存储到ChromaDB
            ids = [f"{filename}_{i}" for i in range(chunk_count)]
            metadatas = [{
                "source": filename,
                "file_path": file_path
            } for _ in range(chunk_count)]

            self.collection.add(
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )

            return {
                "success": True,
                "filename": filename,
                "text_length": text_length,
                "chunk_count": chunk_count,
                "vector_dim": vector_dim
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """语义检索

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        try:
            # 1. 查询向量化
            query_vector = self.embedder.encode([query])[0]

            # 2. ChromaDB检索
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=top_k
            )

            # 3. 格式化结果
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "text": results["documents"][0][i],
                    "source": results["metadatas"][0][i]["source"],
                    "distance": results["distances"][0][i]
                })

            return formatted_results

        except Exception as e:
            raise Exception(f"检索失败: {str(e)}")

    def _split_text(self, text: str) -> list[str]:
        """智能文本分块"""
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size

            # 如果不是最后一块，尝试在标点符号处分割
            if end < text_length:
                for separator in ['。', '！', '？', '\n\n', '；']:
                    sep_pos = text.rfind(separator, start, end)
                    if sep_pos != -1:
                        end = sep_pos + 1
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # 下一块起始位置（保留重叠）
            start = end - self.chunk_overlap

        return chunks

    def get_stats(self) -> dict:
        """获取知识库统计信息"""
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": "medical_knowledge"
            }
        except:
            return {
                "total_chunks": 0,
                "collection_name": "medical_knowledge"
            }
