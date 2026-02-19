"""
RAG 知识检索工具
基于 ChromaDB 实现诈骗案例的向量化存储与检索
"""

import os
import pandas as pd
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGSearchTool:
    """基于 ChromaDB 的反诈知识库检索工具"""
    
    def __init__(
        self,
        persist_dir: str = "./db/chroma",
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        collection_name: str = "scam_cases"
    ):
        """
        初始化 ChromaDB 客户端
        
        Args:
            persist_dir: 数据库持久化目录
            embedding_model: 嵌入模型名称
            collection_name: 集合名称
        """
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        
        # 初始化 ChromaDB
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # 配置嵌入函数（使用 sentence-transformers）
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "反诈骗案例知识库"}
        )
        
        logger.info(f"RAG 知识库已初始化，当前文档数: {self.collection.count()}")
    
    def build_knowledge_base(
        self,
        cases_csv: str = "./data/cases.csv",
        mapping_csv: str = "./data/mapping_full.csv"
    ):
        """
        构建知识库：将案例数据向量化并存入 ChromaDB
        
        Args:
            cases_csv: 案例类型表路径
            mapping_csv: 完整对话映射表路径
        """
        logger.info("开始构建知识库...")
        
        # 清空现有数据（重建模式）
        if self.collection.count() > 0:
            logger.warning("检测到已有数据，将清空后重建...")
            self.client.delete_collection(self.collection.name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection.name,
                embedding_function=self.embedding_function
            )
        
        # 读取案例类型表
        cases_df = pd.read_csv(cases_csv)
        logger.info(f"加载 {len(cases_df)} 个诈骗类型...")
        
        # 读取完整对话数据
        mapping_df = pd.read_csv(mapping_csv)
        logger.info(f"加载 {len(mapping_df)} 个对话样本...")
        
        documents = []
        metadatas = []
        ids = []
        
        # 1. 添加案例类型描述
        for _, row in cases_df.iterrows():
            doc_id = f"case_{row['id']}"
            document = f"诈骗类型：{row['type']}\n描述：{row['desc']}\n关键词：{row['keywords']}"
            
            documents.append(document)
            metadatas.append({
                "source": "cases",
                "case_id": row['id'],
                "case_type": row['type'],
                "keywords": row['keywords']
            })
            ids.append(doc_id)
        
        # 2. 添加典型对话样本（每种类型选前5个）
        for case_id in cases_df['id'].unique():
            samples = mapping_df[mapping_df['case_id'] == case_id].head(5)
            
            for idx, row in samples.iterrows():
                doc_id = f"dialogue_{row['id']}"
                document = f"案例：{row['case_type']}\n对话内容：\n{row['text']}"
                
                documents.append(document)
                metadatas.append({
                    "source": "dialogues",
                    "dialogue_id": row['id'],
                    "case_type": row['case_type'],
                    "risk_level": row['risk_level'],
                    "role_name": row['role_name']
                })
                ids.append(doc_id)
        
        # 批量添加到 ChromaDB
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"✅ 知识库构建完成，共 {len(documents)} 条记录")
        logger.info(f"   - 案例类型: {len(cases_df)} 条")
        logger.info(f"   - 对话样本: {len(documents) - len(cases_df)} 条")
    
    def search_similar_cases(
        self,
        query_text: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        检索与查询文本最相似的案例
        
        Args:
            query_text: 查询文本（通话转录内容）
            top_k: 返回前 K 个最相似结果
            
        Returns:
            [
                {
                    "case_type": "诈骗类型",
                    "document": "相关文档内容",
                    "similarity": 0.85,
                    "metadata": {...}
                },
                ...
            ]
        """
        if self.collection.count() == 0:
            logger.warning("知识库为空，请先调用 build_knowledge_base()")
            return []
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        
        # 格式化结果
        formatted_results = []
        
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "case_type": results['metadatas'][0][i].get('case_type', 'Unknown'),
                    "document": results['documents'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else 0,
                    "metadata": results['metadatas'][0][i]
                })
        
        logger.info(f"检索到 {len(formatted_results)} 个相似案例")
        return formatted_results
    
    def get_case_info(self, case_id: str) -> Optional[Dict]:
        """
        根据案例 ID 获取详细信息
        
        Args:
            case_id: 案例 ID (如 C01)
            
        Returns:
            案例详细信息字典
        """
        results = self.collection.get(
            ids=[f"case_{case_id}"]
        )
        
        if results['ids']:
            return {
                "document": results['documents'][0],
                "metadata": results['metadatas'][0]
            }
        return None


# CrewAI 工具包装器
def search_scam_knowledge(query: str) -> str:
    """
    供 CrewAI Agent 调用的知识检索函数
    
    Args:
        query: 查询文本
        
    Returns:
        格式化的检索结果字符串
    """
    rag_tool = RAGSearchTool()
    results = rag_tool.search_similar_cases(query, top_k=3)
    
    if not results:
        return "未找到相关案例。"
    
    output = "### 相似诈骗案例检索结果：\n\n"
    for i, result in enumerate(results, 1):
        output += f"**匹配 {i}**: {result['case_type']}\n"
        output += f"相关度: {1 - result['distance']:.2f}\n"
        output += f"内容: {result['document'][:200]}...\n\n"
    
    return output


if __name__ == "__main__":
    # 测试代码
    print("\n=== 测试 RAG 知识库 ===\n")
    
    # 初始化工具
    rag = RAGSearchTool()
    
    # 构建知识库
    print("1. 构建知识库...")
    rag.build_knowledge_base(
        cases_csv="../data/cases.csv",
        mapping_csv="../data/mapping_full.csv"
    )
    
    # 测试检索
    print("\n2. 测试检索功能...")
    test_query = "有人打电话说我的银行卡涉嫌洗钱，要求转账到安全账户"
    
    results = rag.search_similar_cases(test_query, top_k=3)
    
    print(f"\n查询: {test_query}\n")
    for i, result in enumerate(results, 1):
        print(f"--- 结果 {i} ---")
        print(f"案例类型: {result['case_type']}")
        print(f"相似度: {1 - result['distance']:.3f}")
        print(f"来源: {result['metadata']['source']}")
        print(f"内容摘要: {result['document'][:100]}...\n")
