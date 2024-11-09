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

model = FlagModel('/Users/caizhuoyue/Desktop/my-langgraph/bge-small-en', use_fp16=True)

# 创建 Qdrant 客户端实例
client = QdrantClient(url="http://localhost:6333")

class APIRetriever():
    def __init__(self):
        self.model_name = "bge-small-en"

    def query_database(self, query: str, mode : str = "api", category : str = "", top_k : int = 5):
        query_embedding = model.encode(query).tolist()
        
        collection_name = f"{mode}_collection_bge_small"
        
        search_result = client.query_points(
        collection_name = collection_name,
        query = query_embedding,
        # 并没有添加
        # 服了爸爸
        # todo
        search_params=models.SearchParams(hnsw_ef=128, exact=False),
        limit=top_k,
        with_payload=True
        ).points

        items = []
        
        for item in search_result:
            items.append({"id": item.id, "score": item.score, "payload": item.payload})

        return items
    
    