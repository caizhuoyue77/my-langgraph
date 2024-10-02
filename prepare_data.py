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
model = FlagModel('/data/czy/bge-small-en', use_fp16=True)

os.environ["CUDA_VISIBLE_DEVICES"] = "2,4,6,7"

# 创建 Qdrant 客户端实例
client = QdrantClient(url="http://localhost:6333")

# 创建一个新的集合（如果集合已经存在，则跳过创建）
client.recreate_collection(
    collection_name="tool_collection_bge_small",
    vectors_config=VectorParams(size=384, distance=Distance.DOT),
)

def load_tool_list(file_path: str) -> List[Dict[str, Any]]:
    """
    从指定的JSON文件加载工具列表。

    :param file_path: str - JSON文件的路径
    :return: List[Dict[str, Any]] - 工具列表
    """ 
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            tool_list = json.load(file)
        print(f"成功加载工具列表，包含 {len(tool_list)} 个工具。")
        return tool_list
    except FileNotFoundError as e:
        raise RuntimeError(f"文件未找到: {e}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"读取JSON文件时出错: {e}") from e

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

def batch_tool_generator(tool_list: List[Dict[str, Any]], batch_size: int = 128) -> Generator[List[Dict[str, Any]], None, None]:
    """
    生成器：按批次生成工具列表以节省内存。

    Args:
        tool_list (List[Dict[str, Any]]): 工具信息列表
        batch_size (int): 每次处理的批次大小

    Yields:
        Generator[List[Dict[str, Any]], None, None]: 批次工具列表
    """
    for i in range(0, len(tool_list), batch_size):
        yield tool_list[i:i + batch_size]

def save_vectors_to_qdrant(vectors: np.ndarray, payloads: List[Dict[str, Any]], start_index: int):
    """
    将向量及其相应的工具信息上传至 Qdrant 数据库中。

    Args:
        vectors (np.ndarray): 编码后的向量矩阵
        payloads (List[Dict[str, Any]]): 对应工具的信息（如工具名称）

    Returns:
        None
    """
    try:
        # 构建要插入Qdrant的点结构
        points = [
            PointStruct(id=i+start_index, vector=vector.tolist(), payload=payload)
            for i, (vector, payload) in enumerate(zip(vectors, payloads))
        ]

        # 执行向量插入操作
        operation_info = client.upsert(
            collection_name="tool_collection_bge_small",
            wait=True,
            points=points
        )
        print(operation_info)
        print(f"成功将 {len(points)} 个向量上传至 Qdrant。")
    except Exception as e:
        print(f"向Qdrant保存向量时失败: {str(e)}")

def compute_and_save_embeddings(tool_list: List[Dict[str, Any]], batch_size: int = 128, mode: str = "tool"):
    """
    计算工具列表的嵌入，并按批次上传至 Qdrant。

    Args:
        tool_list (List[Dict[str, Any]]): 工具列表
        batch_size (int): 批次大小

    Returns:
        None
    """
    print(f"开始计算工具嵌入，总共 {len(tool_list)} 个工具。")
    index = 0
    for tool_batch in batch_tool_generator(tool_list, batch_size=batch_size):
        # 将每个工具的信息拼接成字符串
        if mode == "tool":
            queries = [tool['tool_name'] for tool in tool_batch]
            payloads = [{"tool_name": tool['tool_name'], "category": tool['category'], "tool_description": tool["tool_description"]} for tool in tool_batch]
        elif mode == "api":
            queries = [f"{tool['api_name']}:{tool['api_description']}" for tool in tool_batch]
            payloads = [{"api_name": tool['api_name'], "category": tool['category'], "api_description": tool['api_description'], "tool_name": tool['tool_name']} for tool in tool_batch]
        # 计算嵌入
        embeddings = encode_queries(queries)
        if embeddings.size > 0:
            # 将计算出的嵌入直接保存到 Qdrant 中
            save_vectors_to_qdrant(embeddings, payloads, index)
            index += batch_size


def query():
    embedding_3 = model.encode("weather").tolist()
    
    search_result = client.query_points(
    collection_name="tool_collection_bge_small",
    query=embedding_3,
     
    search_params=models.SearchParams(hnsw_ef=128, exact=False),
    limit=3,
    with_payload=True
    ).points

    print(search_result)


if __name__ == "__main__":
    # 加载工具列表
    tool_list = load_tool_list('/data/czy/Graduation/my-langgraph/rapidapi_all_tools.json')
    # tool_list = load_tool_list('/data/czy/Graduation/my-langgraph/rapidapi_all_apis.json')
    
    # 计算并上传嵌入向量到 Qdrant 数据库
    compute_and_save_embeddings(tool_list)
    
    info = client.get_collection(collection_name="tool_collection_bge_small")
    print(info)
    
    query()
    
    