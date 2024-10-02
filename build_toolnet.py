import json
import networkx as nx
import random
from collections import defaultdict
import copy
from api_retriever import query_database

# 解析JSON文件，提取relevant APIs字段
def parse_toolbench_file(file_path: str) -> list:
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

    return tool_sequences

# 构建基于工具调用顺序的静态图谱，并添加start和end节点
def build_graph_from_json(tool_sequences: list) -> nx.Graph:
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
            # print(tool1)
            # print(tool2)
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

# 根据工具名称查找详细描述
def get_tool_info(tool_name: str, tool_info_path: str) -> dict:
    """
    根据工具名称，在给定的工具信息JSON文件中查找详细描述。
    
    :param tool_name: str - 工具的名称
    :param tool_info_path: str - 存储所有工具描述信息的JSON文件路径
    :return: Dict - 工具的详细信息
    """
    # 读取工具信息文件
    with open(tool_info_path, 'r', encoding='utf-8') as file:
        tool_info_data = json.load(file)

    # 查找工具的详细描述
    for tool in tool_info_data:
        if tool.get('api_name') == tool_name:
            return tool

    return {}

# 随机遍历图中的节点，直到到达end或访问节点数超过20
def traverse_graph(G: nx.Graph, query: str, tool_info_path: str) -> list:
    """
    随机遍历图中的节点，直到到达end节点或访问节点数超过20。
    
    :param G: Graph - 输入图
    :param start_node: str - 起始节点名称
    :param tool_info_path: str - 工具信息文件路径
    :return: List[str] - 访问的节点路径
    """
    nodes = query_database(query, "api")
    node = nodes[0]
    current_node = f'{node["payload"]["tool_name"]}-{node["payload"]["api_name"]}'
    
    # current_node = "Leo Github Data Scraper-Get list of Github repo for Ruby Webscrapping"
    print(current_node)
    path = [current_node]  # 记录访问路径
    visited_count = 0  # 已访问节点数

    while current_node != "end" and visited_count < 20:
        print(f"Current Node: {current_node}")  # 输出当前节点信息

        # 分割节点名称（格式：tool_type-tool_name）
        tool_name = current_node.split('-')[1] if '-' in current_node else current_node

        # 获取工具的详细信息
        tool_info = get_tool_info(tool_name, tool_info_path)
        print(f"Tool Info for {tool_name}: {tool_info}")  # 输出工具详细信息

        # 查找所有邻居（权重大于1）
        neighbors = [
            neighbor for neighbor in G.neighbors(current_node)
            if G[current_node][neighbor].get('weight', 0) >= 1
        ]

        # 如果没有满足条件的邻居，则停止
        if not neighbors:
            print(f"No valid neighbors found for {current_node}. Stopping traversal.")
            break

        # 随机选择一个邻居作为下一个节点
        next_node = random.choice(neighbors)
        print(f"Next Node Selected: {next_node}")

        # 更新路径和当前节点
        path.append(next_node)
        current_node = next_node
        visited_count += 1

    return path

# 主函数
def main():
    # 设置文件路径
    json_file_path = '/Users/caizhuoyue/Desktop/my-langgraph/data/instruction/G1_query.json'
    tool_info_path = '/Users/caizhuoyue/Desktop/my-langgraph/rapidapi_all_apis.json'
    
    json_file_path = './data/instruction/G1_query.json'
    tool_info_path = './rapidapi_all_apis.json'

    # 解析JSON文件，获取工具调用序列
    tool_sequences = parse_toolbench_file(json_file_path)
    
    query = "need Yahoo Finance-earnings"

    # 构建图结构
    G = build_graph_from_json(tool_sequences)
    print(f"Graph Nodes: {len(G.nodes)}")  # 输出图中的节点数量

    # 从start节点开始遍历
    path = traverse_graph(G, query , tool_info_path)
    print(f"Traversal Path: {path}")  # 输出遍历路径

# 执行主函数
if __name__ == "__main__":
    main()