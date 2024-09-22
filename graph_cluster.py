"""
此文件实现Louvain算法聚类功能，并提供从CSV文件构建图的函数。
"""

import pandas as pd
import networkx as nx
import community as community_louvain

def louvain(graph):
    """
    使用Louvain算法对图进行聚类。
    
    :param graph: 包含nodes和edges的字典
    :return: 一个包含簇的列表
    """
    # 创建图对象
    G = nx.Graph()
    for source, target in graph['edges']:
        G.add_edge(source, target)

    # 应用Louvain算法
    partition = community_louvain.best_partition(G)
    
    # 按照簇分组
    clusters = {}
    for node, cluster in partition.items():
        if cluster not in clusters:
            clusters[cluster] = []
        clusters[cluster].append(node)
    
    return list(clusters.values())

def get_graph_from_files(nodes_file, edges_file):
    """
    从CSV文件中读取节点和边，并返回一个字典格式的图。
    
    :param nodes_file: 节点CSV文件路径
    :param edges_file: 边CSV文件路径
    :return: 包含nodes和edges的字典
    """
    nodes_df = pd.read_csv(nodes_file)
    edges_df = pd.read_csv(edges_file)
    
    # 将nodes和edges转换为字典格式
    nodes = nodes_df['name'].tolist()
    edges = list(zip(edges_df['source'], edges_df['target']))
    
    return {
        'nodes': nodes,
        'edges': edges
    }

if __name__ == "__main__":
    # 设置文件路径
    NODES_FILE = 'data/20240921/nodes.csv'
    EDGES_FILE = 'data/20240921/edges.csv'
    
    try:
        # 从文件获取图数据
        graph_data = get_graph_from_files(NODES_FILE, EDGES_FILE)
        
        # 使用Louvain算法进行聚类
        clusters = louvain(graph_data)
        
        # 打印聚类结果
        for i, cluster in enumerate(clusters):
            print(f"簇 {i}: {cluster}")
        
    except FileNotFoundError as e:
        print(f"文件未找到: {e}")
    except pd.errors.EmptyDataError as e:
        print(f"数据为空: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
