import numpy as np
from sentence_transformers import SentenceTransformer
from FlagEmbedding import BGEM3FlagModel, FlagModel
from BCEmbedding import EmbeddingModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any, Generator
import json
import os
import requests

# MODEL_NAMES = ['bge-small-en-v1.5', 'bce', 'toolbench', 'm3e', 'bge']

MODEL_NAMES = ['bge-small-en-v1.5']

SIZES = {'m3e':768, 'bge':1024, 'bge-small-en':384, 'bge-small-en-v1.5': 384, 'bce':768, 'toolbench':768}
MODEL = None
MODEL_NAME = ''


# 创建 Qdrant 客户端实例
client = QdrantClient(url="http://localhost:6333")

def l2_normalize(embeddings):
    """对嵌入进行 L2 归一化"""
    print(f"开始进行 L2 归一化，嵌入矩阵形状: {embeddings.shape}")
    normalized_embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    print("L2 归一化完成")
    return normalized_embeddings

def get_embeddings(sentences: List[str], model_name: str) -> np.ndarray:
    """根据模型名称生成嵌入"""
    url = "http://vnznkz.natappfree.cc/embeddings"
    headers = {"Content-Type": "application/json"}
    data = {
        "sentences": sentences,
        "model_name": model_name
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))

        # 检查请求是否成功
        response.raise_for_status()  # 如果返回状态码不是 200，将引发异常
        
        embeddings = response.json()
        embeddings = embeddings.get("embeddings", []) 
        # print(f"SIZE:{len(embeddings)}")
        # print(f"SIZE:{len(embeddings[0])}")
        embeddings = np.array(embeddings)
        # print(f"EMBEDDING_SIZE:{embeddings.shape()}")
        return embeddings  # 返回 JSON 格式的响应数据
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    

def create_collection_for_model(model_name: str, size: int):
    """根据模型名称创建或重建Qdrant集合"""
    collection_name = f"{model_name}_embedding_collection_1"
    print(f"正在为模型 {model_name} 创建/重建 Qdrant 集合: {collection_name}")
    
    # client.create_collection(
    #     collection_name=collection_name,
    #     vectors_config=VectorParams(size=size, distance=Distance.DOT),
    # )
    
    print(f"Qdrant 集合 {collection_name} 创建/重建成功")
    return collection_name

def save_vectors_to_qdrant(vectors: np.ndarray, payloads: List[Dict[str, Any]], start_index: int, collection_name: str):
    """将向量及其相应的信息上传至 Qdrant 数据库中"""
    print(f"开始向集合 {collection_name} 上传向量数据，起始 ID 为 {start_index}...")
    
    points = [
        PointStruct(id=i+start_index, vector=vector.tolist(), payload=payload)
        for i, (vector, payload) in enumerate(zip(vectors, payloads))
    ]

    operation_info = client.upsert(
        collection_name=collection_name,
        wait=True,
        points=points
    )
    
    print(f"成功上传 {len(points)} 个向量到 Qdrant 集合 {collection_name}: {operation_info}")

def batch_tool_generator(tool_list: List[Dict[str, Any]], batch_size: int = 256) -> Generator[List[Dict[str, Any]], None, None]:
    """生成器：按批次生成工具列表以节省内存"""
    print(f"批量生成工具列表，每批次大小: {batch_size}")
    for i in range(0, len(tool_list), batch_size):
        yield tool_list[i:i + batch_size]

def compute_and_save_embeddings(tool_list: List[Dict[str, Any]], model_name: str, batch_size: int = 256):
    """计算工具列表的嵌入，并按批次上传至 Qdrant"""
    print(f"开始为模型 {model_name} 计算工具嵌入，总共 {len(tool_list)} 个工具，批次大小: {batch_size}")
    
    # 根据模型名称创建/选择集合
    collection_name = create_collection_for_model(f"embedding_{model_name}", SIZES[model_name])
    
    index = 0
    for tool_batch in batch_tool_generator(tool_list, batch_size=batch_size):
        queries = [f"{tool['category_name']} {tool['tool_name']}-{tool['api_name']}:{tool['api_description']}" for tool in tool_batch]
        payloads = [{"api_name": tool['api_name'], "tool_name": tool['tool_name'] ,"category": tool['category_name'], "api_description": tool["api_description"]} for tool in tool_batch]
        
        print(f"正在计算批次工具的嵌入（批次大小: {len(queries)}），从 ID {index} 开始...")
        embeddings = get_embeddings(queries, model_name)
        
        if embeddings.size > 0:
            print(f"嵌入计算完成，开始保存到 Qdrant 集合 {collection_name} 中...")
            save_vectors_to_qdrant(embeddings, payloads, index, collection_name)
            print(f"批次工具向量保存成功，更新索引: {index + len(embeddings)}")
            index += len(embeddings)
        else:
            print(f"嵌入计算失败，跳过该批次")

def load_tool_list(file_path: str) -> List[Dict[str, Any]]:
    """从指定的JSON文件加载工具列表"""
    print(f"正在加载工具列表文件: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            tool_list = json.load(file)
            print(f"工具列表加载成功，包含 {len(tool_list)} 个工具")
            return tool_list
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到")
        return []
    except json.JSONDecodeError:
        print(f"工具列表文件 {file_path} 解析失败")
        return []

if __name__ == "__main__":
    # 加载工具列表
    tool_list = load_tool_list('/Users/caizhuoyue/Desktop/my-langgraph/data/retrieval/G1/unique_apis.json')

    if tool_list:
        # 使用不同模型生成并保存嵌入
        for model_name in MODEL_NAMES:
            print(f"\n=============== 正在处理模型 {model_name} ===============")
            compute_and_save_embeddings(tool_list, model_name=model_name)
            print(f"=============== 模型 {model_name} 处理完成 ===============\n")
    else:
        print("工具列表为空，程序终止")
