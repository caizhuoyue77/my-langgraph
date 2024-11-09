import numpy as np
import os
import json
from typing import List, Dict
from tqdm import tqdm
from FlagEmbedding import FlagModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import SearchParams

model = FlagModel("/Users/caizhuoyue/Documents/code/bge-small-en-v1.5", use_fp16=True)

# 定义模型路径字典
# MODEL_PATHS = {
#     'toolbench': '/Users/caizhuoyue/Documents/code/ToolBench_IR_bert_based_uncased',
#     'bce': '/Users/caizhuoyue/Documents/code/m3e-base',
#     'bge-small-en-v1.5': '/Users/caizhuoyue/Documents/code/bge-small-en-v1.5'
# }


MODEL_PATHS = {
    'bge-small-en-v1.5_tuned': '/Users/caizhuoyue/Documents/code/bge-small-en-v1.5-tuned'
}

# 创建 Qdrant 客户端实例
client = QdrantClient(url="http://localhost:6333")

def initialize_model(model_name: str):
    """
    根据模型名称初始化模型实例。

    Args:
        model_name (str): 模型的名称

    Returns:
        模型实例
    """
    if model_name == 'bge-small-en-v1.5':
        return FlagModel(MODEL_PATHS[model_name], use_fp16=True)
    else:
        return SentenceTransformer(MODEL_PATHS[model_name])

def encode_queries(queries: List[str], model, batch_size: int = 128, max_length: int = 8192) -> np.ndarray:
    """
    对多个字符串进行批量编码，并返回其向量表示。

    Args:
        queries (List[str]): 输入的字符串列表
        model: 模型实例
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

def query(collection_name: str, query: str, top_k: int = 10) -> List[Dict]:
    """
    根据给定的查询在Qdrant集合中进行搜索，并返回前top_k个结果的payload。

    Args:
        query (str): 输入查询文本
        model: 编码模型实例
        top_k (int): 返回的结果数量，默认为前5个

    Returns:
        List[Dict]: 搜索到的结果的payload列表
    """
    global model
    
    embedding = model.encode([query]).tolist()[0]
    
    search_result = client.search(
        collection_name=collection_name,
        query_vector=embedding,
        search_params=SearchParams(hnsw_ef=128, exact=False),
        limit=top_k,
        with_payload=True
    )
    
    # 提取 payload 并返回
    return [{'api_name': point.payload['api_name'], 'tool_name': point.payload['tool_name']} for point in search_result]

def process_queries(collection_name:str, file_path: str, model_name: str, output_file: str):
    """
    处理查询文件，并根据模型搜索相关结果。

    Args:
        file_path (str): 输入查询文件的路径
        model_name (str): 使用的模型名称
        output_file (str): 输出结果的文件路径

    Returns:
        None
    """
    
    results = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(tqdm(f)):
            line_content = line.strip()  # 获取每行内容作为查询
            query_id, query_text = line_content.split('\t', 1)
            query_result = query(collection_name, query_text)  # 搜索相关内容
            
            results.append({
                "query_id": query_id,
                "query": query_text,
                "result": query_result
            })
            print(i)
    
    # 将结果写入JSONL文件
    with open(output_file, 'a', encoding='utf-8') as fout:
        for result in results:
            fout.write(json.dumps(result) + '\n')

if __name__ == "__main__":
    # 输入的文件路径
    input_file = "/Users/caizhuoyue/Desktop/my-langgraph/data/retrieval/G1/train.query.txt"
    
    # 遍历模型列表
    for model_name in MODEL_PATHS.keys():
        # 对于每个模型生成对应的输出文件
        collection_name = "test_embedding_bge_small_v1.5_tuned"
        output_file = f"/Users/caizhuoyue/Desktop/my-langgraph/tuned_small_embedding_{model_name}_1k_results_top10.jsonl"

        # 处理查询文件
        process_queries(collection_name, input_file, model_name, output_file)
        print(f"模型 {model_name} 的结果已保存至 {output_file}")