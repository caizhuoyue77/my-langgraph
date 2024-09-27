import json
import networkx as nx
import matplotlib.pyplot as plt
import community
from collections import defaultdict
import random
import copy
from search_on_graph import bge_m3_similarity

# 获取与查询最相似的邻居
def find_similar_neighbors(G, start_node, query, num_neighbors=10):
    neighbors = list(G.neighbors(start_node))
    similarities = {neighbor: bge_m3_similarity([query], [neighbor])[0][0] for neighbor in neighbors}
    
    # 按相似度排序，选择前 num_neighbors 个
    sorted_neighbors = sorted(similarities.items(), key=lambda item: item[1], reverse=True)[:num_neighbors]
    return [neighbor for neighbor, _ in sorted_neighbors]

def greedy_search_with_similar_neighbors(G, start_node, query, max_nodes=10):
    current_node = start_node
    path = [current_node]

    while len(path) < max_nodes:
        similar_neighbors = find_similar_neighbors(G, current_node, query)
        if not similar_neighbors:
            break
        
        # 贪婪选择权重最大的邻居
        next_node = max(similar_neighbors, key=lambda neighbor: G[current_node][neighbor]['weight'])
        path.append(next_node)
        current_node = next_node

        if current_node == "end":
            break

    return path

def parse_json_file(file_path):
    """
    解析JSON文件，提取relevant APIs字段。
    
    :param file_path: str - JSON文件路径
    :return: List[List[Tuple]] - 返回工具调用序列的列表
    """
    tool_sequences = []
    
    # 读取JSON文件
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # 遍历每个查询，提取relevant APIs
    for entry in data:
        relevant_apis = entry['relevant APIs']
        tool_sequence = relevant_apis
        tool_sequences.append(tool_sequence)
    
    print(tool_sequence)  # 输出最后一条工具调用序列
    return tool_sequences

def build_graph_from_json(tool_sequences):
    """
    构建基于工具调用顺序的静态图谱，并添加start和end节点。
    
    :param tool_sequences: List[List[Tuple]] - 工具调用顺序的列表
    :return: Graph - 构建的无向图
    """
    G = nx.Graph()
    transition_counts = defaultdict(int)  # 记录工具之间的转换次数
    
    # 遍历工具调用序列，记录转换关系
    for sequence in tool_sequences:
        for i in range(len(sequence) - 1):
            tool1 = f"{sequence[i][0]}-{sequence[i][1]}"
            tool2 = f"{sequence[i + 1][0]}-{sequence[i + 1][1]}"
            transition_counts[(tool1, tool2)] += 1
            G.add_edge(tool1, tool2, weight=transition_counts[(tool1, tool2)])
    
    # 添加start和end节点
    start_node = "start"
    end_node = "end"
    
    # 创建 G 的深拷贝
    G_copy = copy.deepcopy(G)  # 深拷贝图 G
    
    # 将start节点连接到所有工具节点
    nodes_list = list(G_copy.nodes())  # 创建节点列表
    for node in nodes_list:
        G_copy.add_edge(start_node, node, weight=1)
    
    # 将end节点连接到所有工具节点
    for node in nodes_list:
        G_copy.add_edge(node, end_node, weight=1)
    
    return G_copy

def sample_graph(G, sample_size=20):
    """
    从图中采样指定数量的节点（包括start和end节点）。
    
    :param G: Graph - 要采样的图
    :param sample_size: int - 采样的节点数量
    :return: Graph - 采样后的子图
    """
    # 确保包含start和end节点
    sampled_nodes = {"start", "end"}
    
    # 从其他节点中随机采样
    other_nodes = list(G.nodes())
    other_nodes.remove("start")
    other_nodes.remove("end")
    
    # 如果其他节点数量不足，使用所有其他节点
    if len(other_nodes) <= (sample_size - 2):
        sampled_nodes.update(other_nodes)
    else:
        sampled_nodes.update(random.sample(other_nodes, sample_size - 2))
    
    # 创建子图
    sampled_graph = G.subgraph(sampled_nodes)
    
    return sampled_graph

def calculate_weights_stats(G):
    """
    计算图中边的权重的最大值、最小值和平均值。
    
    :param G: Graph - 输入图
    :return: Tuple[float, float, float] - (最大值, 最小值, 平均值)
    """
    weights = [data['weight'] for _, _, data in G.edges(data=True)]  # 提取所有边的权重

    if not weights:  # 如果没有边，则返回0
        return 0, 0, 0

    max_weight = max(weights)  # 最大值
    min_weight = min(weights)  # 最小值
    avg_weight = sum(weights) / len(weights)  # 平均值
    
    return max_weight, min_weight, avg_weight

def beam_search(G, start, end, beam_size=3):
    """
    从start节点到end节点进行Beam Search，返回权重最大路径
    
    :param G: Graph - 输入图
    :param start: str - 起始节点
    :param end: str - 结束节点
    :param beam_size: int - 每层保留的路径数量
    :return: Tuple[List[str], float] - 权重最大路径及其权重
    """
    # 初始化路径和权重
    paths = [(start, 0, [start])]  # (当前节点, 当前权重, 路径)

    while paths:
        new_paths = []
        
        for path in paths:
            current_node, current_weight, current_route = path
            
            # 如果当前路径的节点数量超过10，则结束搜索
            if len(current_route) > 10:
                continue
            
            # 遍历当前节点的邻居
            for neighbor in G.neighbors(current_node):
                weight = G[current_node][neighbor]['weight']
                new_weight = current_weight + weight
                new_route = current_route + [neighbor]
                
                # 如果到达end节点，记录路径
                if neighbor == end:
                    return new_route, new_weight  # 直接返回路径和权重
                
                new_paths.append((neighbor, new_weight, new_route))
        
        # 按权重排序并保留前beam_size个路径
        new_paths = sorted(new_paths, key=lambda x: x[1], reverse=True)[:beam_size]
        paths = new_paths

        # 如果没有新路径，结束搜索
        if not paths:
            break

    # 找到权重最大路径
    if paths:
        best_path = max(paths, key=lambda x: x[1])
        return best_path[2], best_path[1]  # 返回路径和权重
    else:
        return [], 0

def greedy_search(G, start, end):
    """
    从start节点到end节点进行贪心搜索，返回路径和权重
    
    :param G: Graph - 输入图
    :param start: str - 起始节点
    :param end: str - 结束节点
    :return: Tuple[List[str], float] - 权重路径及其权重
    """
    current_node = start
    current_weight = 0
    path = [current_node]
    visited = {current_node}  # 使用集合跟踪已访问的节点

    while current_node != end:
        # 如果当前路径的节点数量超过10，则结束搜索
        if len(path) > 10:
            print("节点数量超过10，搜索结束。")
            return path, current_weight
        
        # 获取当前节点的所有邻居
        neighbors = list(G.neighbors(current_node))
        # 过滤掉已经访问过的邻居
        unvisited_neighbors = [n for n in neighbors if n not in visited]

        if not unvisited_neighbors:  # 如果没有可访问的邻居，则退出循环
            print("当前节点没有可访问的邻居，搜索结束。")
            break
        
        # 找到权重最大的未访问邻居
        max_weight_neighbor = max(unvisited_neighbors, key=lambda neighbor: G[current_node][neighbor]['weight'])
        weight_to_neighbor = G[current_node][max_weight_neighbor]['weight']

        # 更新当前路径和权重
        current_weight += weight_to_neighbor
        current_node = max_weight_neighbor
        path.append(current_node)
        visited.add(current_node)  # 标记当前节点为已访问

        # 打印当前路径和权重
        print(f"当前路径: {path}, 当前权重: {current_weight}")

    return path, current_weight

def louvain_clustering(G, resolution=1.0):
    """
    使用Louvain算法对图进行聚类

    :param G: Graph - 输入图
    :return: Dict - 节点与其聚类的映射
    """
    partition = communitybest_partition(G, resolution=resolution)  # 执行Louvain聚类
    return partition


def draw_graph_with_communities(G, partition):
    """
    可视化图谱，显示聚类结果
    
    :param G: Graph - 要绘制的图
    :param partition: Dict - 节点与其聚类的映射
    """
    pos = nx.spring_layout(G)
    cmap = plt.get_cmap('viridis', max(partition.values()) + 1)  # 根据聚类数量选择颜色

    # 绘制节点
    nx.draw(G, pos, node_color=[cmap(partition[node]) for node in G.nodes()],
            with_labels=True, node_size=300, font_size=5)

    # 绘制边
    weights = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=weights)
    
    plt.title("Louvain Clustering")
    plt.show()
    
def print_cluster_info(partition):
    """
    打印聚类信息，包括聚类数量、每个聚类的节点数量及具体节点

    :param partition: Dict - 节点与其聚类的映射
    """
    cluster_dict = defaultdict(list)

    # 将节点按聚类分组
    for node, cluster in partition.items():
        cluster_dict[cluster].append(node)

    # 打印聚类数量
    print(f"总共的聚类数量: {len(cluster_dict)}")
    
    # 打印每个聚类的信息
    for cluster_id, nodes in cluster_dict.items():
        print(f"聚类 {cluster_id}: 节点数量 {len(nodes)}, 节点: {nodes}")

def count_clusters(partition):
    """
    计算聚类中的簇的数量

    :param partition: Dict - 节点与其聚类的映射
    :return: int - 簇的数量
    """
    unique_clusters = set(partition.values())  # 获取唯一簇标识
    return len(unique_clusters)  # 返回唯一簇的数量
 
 # 执行Louvain聚类
def perform_louvain_clustering(G):
    partition = community.best_partition(G)
    clusters = {}
    for node, cluster_id in partition.items():
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(node)
    return clusters

# 获取最相似的cluster
def get_most_similar_cluster(query: str, clusters: dict) -> int:
    best_cluster_id = None
    best_similarity = -1

    for cluster_id, nodes in clusters.items():
        # 计算cluster的summary
        cluster_summary = " ".join(nodes)  # 可以根据需要调整summary的定义
        similarity = bge_m3_similarity([query], [cluster_summary])[0][0]
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_cluster_id = cluster_id

    return best_cluster_id

# 示例用法
json_file_path = '/Users/caizhuoyue/Desktop/my-langgraph/data/instruction/G1_query.json'

# 解析JSON文件，提取工具调用序列
tool_sequences = parse_json_file(json_file_path)

# 构建图谱
G = build_graph_from_json(tool_sequences)

# print(f"Nodes:{len(G.nodes)}")

# 计算并输出边权重的统计信息
# max_weight, min_weight, avg_weight = calculate_weights_stats(G)
# print(f"Max Weight: {max_weight}")
# print(f"Min Weight: {min_weight}")
# print(f"Average Weight: {avg_weight}")

# 采样图谱
sampled_G = sample_graph(G, sample_size=100)

# 输出采样的节点和边的数量
# print(f"Sampled Nodes: {len(sampled_G.nodes)}")
# print(f"Sampled Edges: {len(sampled_G.edges)}")

# 使用Beam Search从start到end
# best_path, total_weight = beam_search(G, "start", "end", beam_size=3)

# print("\n== Beam Search ==")
# print(f"Best Path: {best_path}")
# print(f"Total Weight: {total_weight}")
# print("=================")


# 使用贪心搜索从start到end
# best_path, total_weight = greedy_search(G, "start", "end")

# print("\n== Greedy Search ==")
# print(f"最终路径: {best_path}")
# print(f"总权重: {total_weight}")
# print("===================")


# 使用Louvain算法进行聚类
# partition = louvain_clustering(G, 2.0)
# print(f"一共有{count_clusters(partition)}个cluster")

# 打印聚类结果及其信息
# print("节点与聚类的映射：")
# print_cluster_info(partition)

# 可视化图谱及其聚类
# draw_graph_with_communities(G, partition)

def draw_graph(G):
    """
    可视化图谱，显示工具及其转换边的权重。
    
    :param G: Graph - 要绘制的图
    """
    pos = nx.spring_layout(G)  # 使用弹簧布局
    weights = nx.get_edge_attributes(G, 'weight')  # 获取边的权重
    nx.draw(G, pos, with_labels=True, node_color='lightgreen', node_size=300, font_size=5)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=weights)  # 显示边的权重标签
    plt.show()  # 展示图形

# 调用可视化函数
# draw_graph(sampled_G)

start_node = "start"
query = "weather forcast"

# 执行贪婪搜索
# result_path = greedy_search_with_similar_neighbors(G, start_node, query)
# print(f"Greedy Search Path: {result_path}")


# 执行Louvain聚类
"""
该模块用于对图进行Louvain聚类，并随机抽取k个社区（cluster）。
"""

import random
import community as community_louvain  # 需要安装python-louvain库

def perform_louvain_clustering(G, k: int):
    """
    对图进行Louvain聚类，并随机返回k个社区。
    
    参数:
    G (nx.Graph): 输入的图
    k (int): 要随机抽取的社区数量
    
    返回:
    dict: k个随机抽取的社区及其对应的节点
    """
    # 执行Louvain聚类，得到每个节点所属的社区ID
    partition = community_louvain.best_partition(G)
    
    # 根据partition组织社区
    clusters = {}
    for node, cluster_id in partition.items():
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(node)
    
    # 随机抽取k个社区
    num_clusters = len(clusters)
    if k > num_clusters:
        raise ValueError(f"指定的k值 {k} 超过了社区数量 {num_clusters}")
    
    sampled_cluster_ids = random.sample(list(clusters.keys()), k)
    
    # 返回抽取的k个社区及其节点
    sampled_clusters = {cluster_id: clusters[cluster_id] for cluster_id in sampled_cluster_ids}
    
    return sampled_clusters

# 获取最相似的cluster
def get_most_similar_cluster(query: str, clusters: dict) -> int:
    best_cluster_id = None
    best_similarity = -1

    for cluster_id, nodes in clusters.items():
        # 计算cluster的summary
        cluster_summary = " ".join(nodes)  # 可以根据需要调整summary的定义
        similarity = bge_m3_similarity([query], [cluster_summary])[0][0]
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_cluster_id = cluster_id

    return best_cluster_id

# 定义获取最相似的前k个cluster的函数
def get_top_k_similar_clusters(query: str, clusters: dict, k: int) -> list:
    # 存储簇的相似度与ID
    similarities = []

    for cluster_id, nodes in clusters.items():
        # 计算cluster的summary
        cluster_summary = " ".join(nodes)  # 可以根据需要调整summary的定义
        similarity = bge_m3_similarity([query], [cluster_summary])[0][0]
        similarities.append((similarity, cluster_id, nodes))  # 存储相似度、ID和内容

    # 按照相似度排序并取前k个
    top_k = sorted(similarities, key=lambda x: x[0], reverse=True)[:k]
    
    return top_k  # 返回包含相似度、ID和内容的元组

clusters = perform_louvain_clustering(G, 50)

# print("Clusters found:", clusters)

# 查询
query = "what's the weather like today?"

query = "what's the calories of french fries?"

# 调用获取最相似的前k个cluster的函数

k = 5
top_k_clusters = get_top_k_similar_clusters(query, clusters, k)

# 打印结果
for similarity, cluster_id, nodes in top_k_clusters:
    print(f"Cluster ID: {cluster_id}, 内容: {nodes}, 相似度: {similarity:.4f}")

# 获取最相似的cluster
# most_similar_cluster_id = get_most_similar_cluster(query, clusters)
# print(f"========\nMost Similar Cluster ID: {most_similar_cluster_id}, Nodes: {clusters[most_similar_cluster_id]}\n=======")