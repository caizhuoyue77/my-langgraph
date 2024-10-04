import json
import networkx as nx
import random
from collections import defaultdict
import copy
from api_retriever import query_database
from algos.qwen25_7b import get_qwen25_7b

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
import json
import networkx as nx
import copy
from collections import defaultdict

def build_graph_from_json(tool_sequences: list, api_info_file: str) -> nx.Graph:
    """
    构建基于工具调用顺序的静态图谱，并添加start和end节点。
    
    :param tool_sequences: List[List[Tuple]] - 工具调用顺序的列表
    :param api_info_file: str - rapidapi_all_apis.json文件路径
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

    # 遍历整个rapidapi_all_apis.json文件，添加API节点
    with open(api_info_file, 'r', encoding='utf-8') as api_file:
        api_data = json.load(api_file)

        for api_entry in api_data:
            tool_name = api_entry.get('tool_name', '')
            api_name = api_entry.get('api_name', '')
            if tool_name and api_name:
                api_node = f"{tool_name}-{api_name}"
                if api_node not in G:
                    G.add_node(api_node)  # 如果图中没有该节点则添加

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
    :param query: str - 查询字符串
    :param tool_info_path: str - 工具信息文件路径
    :return: List[str] - 访问的节点路径
    """
    nodes = query_database(query, "api")
    if not nodes:
        print("No nodes found for the given query.")
        return []

    # 调用 LLM 选择初始节点
    neighbors = [f'{node["payload"]["tool_name"]}-{node["payload"]["api_name"]}' for node in nodes]
    current_node = choose_neighbor(query, [], neighbors)

    if not current_node:
        print("No valid start node selected.")
        return []

    print(f"Starting Node: {current_node}")
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
        
        print("All neighbors")
        print(neighbors)

        # 如果没有满足条件的邻居，则停止
        if not neighbors:
            print(f"No valid neighbors found for {current_node}. Stopping traversal.")
            break

        # 调用choose_neighbor函数
        next_node = choose_neighbor(query, path, neighbors)
        if next_node is None:
            print("选择的下一个节点无效，停止遍历。")
            break

        print(f"Next Node Selected: {next_node}")

        # 更新路径和当前节点
        path.append(next_node)
        current_node = next_node
        visited_count += 1

    return path


def choose_neighbor(query, path, neighbors):
    """
    根据当前路径和邻居节点，调用 LLM 选择下一个节点。
    
    :param path: List[str] - 当前已访问路径
    :param neighbors: List[str] - 可选择的邻居节点
    :return: str - 选择的下一个邻居节点
    """
    llm = get_qwen25_7b()
    
    prompt = f"""
    
    为了完成任务:{query}
    
    # 历史工具调用记录
    {path}
    
    # 当前可选工具
    {neighbors}
    
    请你选择下*一*个工具。注意只能选一个。
    直接输出工具的名称，不要有额外的内容输出。
    如果你认为历史工具调用已经可以完成任务，请你输出end。
    """
    
    print(prompt)
    
    ans = llm.invoke(prompt)
    
    print("")
    print(ans)
    
    if ans in neighbors:
        return ans
    
    return None

# 主函数
def main():
    # 设置文件路径
    json_file_path = '/Users/caizhuoyue/Desktop/my-langgraph/data/instruction/G1_query.json'
    tool_info_path = '/Users/caizhuoyue/Desktop/my-langgraph/rapidapi_all_apis.json'
    
    json_file_path = './data/instruction/G1_query.json'
    tool_info_path = './rapidapi_all_apis.json'

    # 解析JSON文件，获取工具调用序列
    tool_sequences = parse_toolbench_file(json_file_path)
    
    query = "what's the recipe of chicken soup and the weather in changsha"

    # 构建图结构
    G = build_graph_from_json(tool_sequences, './rapidapi_all_apis.json')
    print(f"Graph Nodes: {len(G.nodes)}")  # 输出图中的节点数量

    # 从start节点开始遍历
    path = traverse_graph(G, query, tool_info_path)
    print(f"Traversal Path: {path}")  # 输出遍历路径

# 执行主函数
if __name__ == "__main__":
    main()
