import json
import networkx as nx
import random
from collections import defaultdict
import copy
from api_retriever import APIRetriever
from algos.qwen25_7b import get_qwen25_7b
from task_decomposer import Decomposer


retriever = APIRetriever()

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
def traverse_graph(G: nx.Graph, query: str, tool_info_path: str, category: str) -> list:
    """
    随机遍历图中的节点，直到到达end节点或访问节点数超过20。
    
    :param G: Graph - 输入图
    :param query: str - 查询字符串
    :param tool_info_path: str - 工具信息文件路径
    :return: List[str] - 访问的节点路径
    """
    nodes = retriever.query_database(query, "api", category)
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

        tool_name = current_node.split('-')[1] if '-' in current_node else current_node

        tool_info = get_tool_info(tool_name, tool_info_path)
        print(f"Tool Info for {tool_name}: {tool_info}")  # 输出工具详细信息

        # 查找所有邻居（权重大于1，排除 start 和 end）
        neighbors = [
            neighbor for neighbor in G.neighbors(current_node)
            if G[current_node][neighbor].get('weight', 0) >= 1 and neighbor not in ["start", "end"]
        ]
        
        print("Filtered neighbors (excluding 'start' and 'end'):")
        print(neighbors)

        # 如果邻居数量超过5个，随机选择5个邻居
        if len(neighbors) > 5:
            neighbors = random.sample(neighbors, 5)

        # 如果邻居数量不足5个，并且只有start、end或邻居数量在1-4个，调用query_database再添加5个邻居
        elif len(neighbors) < 5:
            print(f"Adding neighbors from query_database for {current_node}")
            new_neighbors = retriever.query_database(query, "api")
            for new_neighbor in new_neighbors:
                neighbor_node = f'{new_neighbor["payload"]["tool_name"]}-{new_neighbor["payload"]["api_name"]}'
                if neighbor_node not in neighbors:
                    neighbors.append(neighbor_node)
                if len(neighbors) >= 5:
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
    
    prompt = f"""你是一个非常专业和睿智的计算机学生，你负责调用API工具来完成任务。
# 现有任务
{query}

# 请你从下列工具中选择1个，作为本次调用的工具
{neighbors}
end

# 已经选择的工具（不用重复选）
{path}

# 注意
1.请你直接输出工具名称，不要有额外的输出。
2.如果你认为已经选择的工具组可以完成任务，那么你不需要选择新工具，直接输出end。
3.注意，一次只能选择一个
4.如果有多个都可以完成，选择最合适的一个。
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
    
    # 构建图结构
    G = build_graph_from_json(tool_sequences, './rapidapi_all_apis.json')
    print(f"No. of Graph Nodes: {len(G.nodes)}")  # 输出图中的节点数量
    
    query = "what's the recipe of chicken soup and the weather in changsha"
    
    decomposer = Decomposer("qwen2.5:7b", query)
    sub_tasks = decomposer.run()
    
    for sub_task in sub_tasks:
        print("=======================")
        print(sub_task)
        print("=======================")
        # 从start节点开始遍历
        path = traverse_graph(G, f"{sub_task['name']}:{sub_task['description']}", tool_info_path, sub_task['category'])
        print(f"Traversal Path: {path}")  # 输出遍历路径

# 执行主函数
if __name__ == "__main__":
    main()
