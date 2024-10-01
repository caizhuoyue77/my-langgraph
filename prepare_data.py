"""
本脚本用于使用 BGEM3FlagModel 对输入字符串进行编码，并将生成的向量保存到 .npy 文件中。
"""
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


model = FlagModel('/data/czy/bge-small-en', use_fp16=True)

os.environ["CUDA_VISIBLE_DEVICES"]="2,4,7"

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
    

def encode_queries(queries: List[str], batch_size: int = 32, max_length: int = 8192) -> np.ndarray:
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
    

def compute_and_save_embeddings(tool_list: List[Dict[str, Any]], save_path: str, batch_size: int = 128):
    """
    计算工具列表的嵌入，并按批次保存到指定路径。

    Args:
        tool_list (List[Dict[str, Any]]): 工具列表
        save_path (str): 保存路径
        batch_size (int): 批次大小

    Returns:
        None
    """
    print(f"开始计算工具嵌入，总共 {len(tool_list)} 个工具。")
    batch_index = 129
    for tool_batch in batch_tool_generator(tool_list, batch_size=batch_size):
        # 将每个工具的信息拼接成字符串
        queries = [f"{tool['tool_name']} {tool['tool_description']}" for tool in tool_batch]
        payloads = [{"tool_name": tool['tool_name'] for tool in tool_batch}]
        # 计算嵌入
        embeddings = encode_queries(queries)
        if embeddings.size > 0:
            save_vectors_to_qdrant(embeddings, payloads)
        batch_index += 1


import numpy as np

client = QdrantClient(url="http://localhost:6333")



info = client.create_collection(
    collection_name="api_collection_1",
    vectors_config=VectorParams(size=1024, distance=Distance.DOT),
)



# 定义模型实例（全局只初始化一次）
model = FlagModel('/data/czy/bge-small-en', use_fp16=True)

os.environ["CUDA_VISIBLE_DEVICES"]="7"

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

def encode_queries(queries: List[str], batch_size: int = 64, max_length: int = 8192) -> np.ndarray:
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

def batch_tool_generator(tool_list: List[Dict[str, Any]], batch_size: int = 64) -> Generator[List[Dict[str, Any]], None, None]:
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

def save_vectors_to_npy(vectors: np.ndarray, save_path: str, batch_index: int):
    """
    将向量矩阵保存为 .npy 文件，并使用批次索引来管理文件名。

    Args:
        vectors (np.ndarray): 编码后的向量矩阵
        save_path (str): 保存的文件基础路径
        batch_index (int): 批次索引

    Returns:
        None
    """
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        batch_save_path = f"{save_path}_batch_{batch_index}.npy"
        np.save(batch_save_path, vectors, allow_pickle=True)
        print(f"批次 {batch_index} 向量成功保存至文件: {batch_save_path}")
    except Exception as e:
        print(f"保存向量文件失败: {str(e)}")

def compute_and_save_embeddings(tool_list: List[Dict[str, Any]], save_path: str, batch_size: int = 128):
    """
    计算工具列表的嵌入，并按批次保存到指定路径。

    Args:
        tool_list (List[Dict[str, Any]]): 工具列表
        save_path (str): 保存路径
        batch_size (int): 批次大小

    Returns:
        None
    """
    print(f"开始计算工具嵌入，总共 {len(tool_list)} 个工具。")
    batch_index = 0
    for tool_batch in batch_tool_generator(tool_list, batch_size=batch_size):
        # 将每个工具的信息拼接成字符串
        queries = [f"{tool['tool_name']} {tool['api_description']}" for tool in tool_batch]
        # 计算嵌入
        embeddings = encode_queries(queries)
        
        print(embeddings)
        
        if embeddings.size > 0:
            save_vectors_to_npy(embeddings, save_path, batch_index)
        batch_index += 1


def save_vectors_to_npy(vectors: np.ndarray, save_path: str, batch_index: int):
    pass
    
if __name__ == "__main__":
    # 加载工具列表
    tool_list = load_tool_list('/data/czy/Graduation/my-langgraph/rapidapi_all_apis.json')
    
    # 定义保存路径
    save_path = "/data/czy/Graduation/my-langgraph/tool_embeddings_2/tool_embeddings"

    # 计算并保存嵌入向量
    compute_and_save_embeddings(tool_list, save_path)