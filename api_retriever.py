# 获取k个最相似的api

import numpy as np
import pandas as pd
from FlagEmbedding import FlagModel
from tqdm import tqdm
import os
import json
from typing import List, Dict, Any, Generator

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from qdrant_client.models import Filter, FieldCondition, MatchValue
from qdrant_client import QdrantClient, models


# 定义模型实例（全局只初始化一次）
# model = FlagModel('/data/czy/bge-small-en', use_fp16=True)

model = FlagModel('./bge-small-en', use_fp16=True)

os.environ["CUDA_VISIBLE_DEVICES"] = "2,4,6,7"

# 创建 Qdrant 客户端实例
client = QdrantClient(url="http://localhost:6333")

# 创建一个新的集合（如果集合已经存在，则跳过创建）

def encode_queries(queries: List[str], batch_size: int = 128, max_length: int = 8192) -> np.ndarray:
    """
    对多个字符串进行批量编码，并返回其向量表示。

    Args:
        queries (List[str]): 输入的字符串列表
        batch_size (int): 模型编码时的批次大小
        max_length (int): 最大编码长度

    Returns:
        np.ndarray: 编码后的向量矩阵
    """
    try:
        embeddings = model.encode(queries)
        return np.array(embeddings)
    except Exception as e:
        print(f"编码失败: {str(e)}")
        return np.array([])


def query_llm():
    # toolbench自己训练的那个retriever
    
    from sentence_transformers import SentenceTransformer
    sentences = ["This is an example sentence", "Each sentence is converted"]

    model = SentenceTransformer('/data/czy/ToolBench_IR_bert_based_uncased')
    embeddings = model.encode(sentences)
    print(embeddings)


    # pass

def query_database(query: str, mode : str = "api", top_k : int = 8, category : str = ""):
    query_embedding = model.encode(query).tolist()
    
    collection_name = f"{mode}_collection_bge_small"
    
    search_result = client.query_points(
    collection_name = collection_name,
    query = query_embedding,
    search_params=models.SearchParams(hnsw_ef=128, exact=False),
    
    limit=top_k,
    with_payload=True
    ).points

    items = []
    
    for item in search_result:
        items.append({"id": item.id, "score": item.score, "payload": item.payload})

    return items

if __name__ == "__main__":
    # items = query("whats the weather like today in Beijing?")
    # print(items)
    query_llm()
    
    