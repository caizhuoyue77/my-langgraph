import json
import tiktoken
import os
from typing import List, Callable
from datetime import datetime
from FlagEmbedding import BGEM3FlagModel, FlagReranker

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    计算文本在指定模型中的token数量。

    Args:
        text (str): 需要计算的文本
        model (str): 使用的模型名称，默认是 "gpt-3.5-turbo"

    Returns:
        int: 文本中的token数量
    """
    try:
        encoder = tiktoken.encoding_for_model(model)
    except KeyError as e:
        raise ValueError(f"无效的模型名称: {model}, 错误信息: {e}")
    
    tokens = encoder.encode(text)
    return len(tokens)


# bge-m3 embedding
def bge_m3_embedding(sentences_1: List[str]) -> List[float]:
    """
    使用BGE M3模型计算两个句子列表之间的相似度。

    Args:
        sentences_1 (List[str]): 第一个句子列表
        sentences_2 (List[str]): 第二个句子列表

    Returns:
        List[List[float]]: 相似度矩阵
    """
    model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

    embeddings_1 = model.encode(sentences_1,
                                batch_size=12, 
                                max_length=8192)['dense_vecs']
    
    return embeddings_1

# bge-m3
def bge_m3_similarity(sentences_1: List[str], sentences_2: List[str]) -> List[List[float]]:
    """
    使用BGE M3模型计算两个句子列表之间的相似度。

    Args:
        sentences_1 (List[str]): 第一个句子列表
        sentences_2 (List[str]): 第二个句子列表

    Returns:
        List[List[float]]: 相似度矩阵
    """
    model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

    embeddings_1 = model.encode(sentences_1, 
                                 batch_size=12, 
                                 max_length=8192)['dense_vecs']
    embeddings_2 = model.encode(sentences_2)['dense_vecs']
    
    similarity = embeddings_1 @ embeddings_2.T
    return similarity

# bge-reranker
def bge_rerank(query: str, passages: List[str], normalize: bool = False) -> List[float]:
    """
    使用BGE Reranker计算查询和多个段落之间的评分。

    Args:
        query (str): 查询文本
        passages (List[str]): 段落列表
        normalize (bool): 是否将评分归一化到0-1之间

    Returns:
        List[float]: 段落评分列表
    """
    reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)
    
    scores = reranker.compute_score([[query, passage] for passage in passages], normalize=normalize)
    return scores

# 对每个cluster的summary计算相似度
def get_clusters(query: str, clusters: List[dict], top_k: int):
    """
    从所有cluster中获取最相似的clusters。

    Args:
        query (str): 查询文本
        clusters (List[dict]): 包含cluster信息的字典列表
        top_k (int): 选择的top K个相似度最高的clusters

    Returns:
        List[dict]: 选择的clusters
    """
    # 提取cluster的summary
    cluster_summaries = [cluster['summary'] for cluster in clusters]
    
    # 计算相似度
    similarity_matrix = bge_m3_similarity([query], cluster_summaries)
    
    # 获取top K的cluster索引
    top_indices = similarity_matrix[0].argsort()[-top_k:][::-1]
    
    # 选出对应的clusters
    selected_clusters = [clusters[i] for i in top_indices]
    
    return selected_clusters

if __name__ == '__main__':
    # 示例查询
    query = "What is BGE?"
    
    print(bge_m3_embedding([query]))

    # 示例clusters，每个cluster包含名称和summary
    # clusters = [
    #     {"name": "Cluster 1", "summary": "BGE M3 is an embedding model supporting dense retrieval."},
    #     {"name": "Cluster 2", "summary": "BM25 is a ranking function used in information retrieval."},
    #     {"name": "Cluster 3", "summary": "BGE Reranker improves the scoring of retrieval results."},
    #     {"name": "Cluster 4", "summary": "Embedding models are crucial for modern NLP tasks."},
    #     {"name": "Cluster 5", "summary": "Dense retrieval uses vector representations to find similar documents."}
    # ]

    # # 获取与查询最相似的clusters，选择top 3个
    # top_k = 3
    # selected_clusters = get_clusters(query, clusters, top_k)

    # # 打印结果
    # print("Selected Clusters:")
    # for cluster in selected_clusters:
    #     print(f"- Name: {cluster['name']}, Summary: {cluster['summary']}")

