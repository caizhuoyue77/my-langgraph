import json
import networkx as nx
import random
from collections import defaultdict
import copy
from api_retriever import APIRetriever
from qwen25_7b import get_qwen25_7b
from task_decomposer import Decomposer


class GraphTraversal:
    def __init__(self, json_file_path: str, tool_info_path: str):
        """
        初始化 GraphTraversal 类，设置 JSON 文件路径和工具信息文件路径，并初始化 APIRetriever 实例。
        
        :param json_file_path: str - JSON 文件路径
        :param tool_info_path: str - 工具信息 JSON 文件路径
        """
        self.json_file_path = json_file_path
        self.tool_info_path = tool_info_path
        self.retriever = APIRetriever()

    def parse_toolbench_file(self) -> list:
        """
        解析JSON文件，提取relevant APIs字段。
        
        :return: List[List[Tuple]] - 返回工具调用序列的列表
        """
        tool_sequences = []
        with open(self.json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for entry in data:
            relevant_apis = entry['relevant APIs']
            tool_sequence = relevant_apis
            tool_sequences.append(tool_sequence)

        return tool_sequences

    def build_graph_from_json(self, tool_sequences: list) -> nx.Graph:
        """
        构建基于工具调用顺序的静态图谱，并添加start和end节点。
        
        :param tool_sequences: List[List[Tuple]] - 工具调用顺序的列表
        :return: Graph - 构建的无向图
        """
        G = nx.Graph()
        transition_counts = defaultdict(int)

        for sequence in tool_sequences:
            for i in range(len(sequence) - 1):
                tool1 = f"{sequence[i][0]}-{sequence[i][1]}"
                tool2 = f"{sequence[i + 1][0]}-{sequence[i + 1][1]}"
                transition_counts[(tool1, tool2)] += 1
                G.add_edge(tool1, tool2, weight=transition_counts[(tool1, tool2)])

        start_node = "start"
        end_node = "end"

        with open(self.tool_info_path, 'r', encoding='utf-8') as api_file:
            api_data = json.load(api_file)
            for api_entry in api_data:
                tool_name = api_entry.get('tool_name', '')
                api_name = api_entry.get('api_name', '')
                if tool_name and api_name:
                    api_node = f"{tool_name}-{api_name}"
                    if api_node not in G:
                        G.add_node(api_node)

        G_copy = copy.deepcopy(G)
        nodes_list = list(G_copy.nodes())

        for node in nodes_list:
            G_copy.add_edge(start_node, node, weight=1)

        for node in nodes_list:
            G_copy.add_edge(node, end_node, weight=1)

        return G_copy

    def get_tool_info(self, tool_name: str) -> dict:
        """
        根据工具名称，在给定的工具信息JSON文件中查找详细描述。
        
        :param tool_name: str - 工具的名称
        :return: Dict - 工具的详细信息
        """
        with open(self.tool_info_path, 'r', encoding='utf-8') as file:
            tool_info_data = json.load(file)

        for tool in tool_info_data:
            if tool.get('api_name') == tool_name:
                return tool

        return {}

    def traverse_graph(self, G: nx.Graph, query: str, category: str) -> list:
        """
        随机遍历图中的节点，直到到达end节点或访问节点数超过20。
        
        :param G: Graph - 输入图
        :param query: str - 查询字符串
        :param category: str - 查询类别
        :return: List[str] - 访问的节点路径
        """
        nodes = self.retriever.query_database(query, "api", category)
        if not nodes:
            print("No nodes found for the given query.")
            return []

        neighbors = [f'{node["payload"]["tool_name"]}-{node["payload"]["api_name"]}' for node in nodes]
        current_step = self.choose_neighbor(query, [], neighbors)
        
        current_node = current_step.get("action", None)
        
        print("~~~~~~~~~~~~~~~~~~~~~~")
        print(current_node)
        print("~~~~~~~~~~~~~~~~~~~~~~")

        if not current_node:
            print("No valid start node selected.")
            return []

        print(f"Starting Node: {current_node}")
        path = [current_node]
        visited_count = 0

        while current_node != "end" and visited_count < 20:
            print(f"Current Node: {current_node}")

            tool_name = current_node.split('-')[1] if '-' in current_node else current_node
            tool_info = self.get_tool_info(tool_name)
            print(f"Tool Info for {tool_name}: {tool_info}")

            neighbors = [
                neighbor for neighbor in G.neighbors(current_node)
                if G[current_node][neighbor].get('weight', 0) >= 1 and neighbor not in ["start", "end"]
            ]

            print("Filtered neighbors (excluding 'start' and 'end'):")
            print(neighbors)

            if len(neighbors) > 5:
                neighbors = random.sample(neighbors, 5)
            elif len(neighbors) < 5:
                print(f"Adding neighbors from query_database for {current_node}")
                new_neighbors = self.retriever.query_database(query, "api")
                for new_neighbor in new_neighbors:
                    neighbor_node = f'{new_neighbor["payload"]["tool_name"]}-{new_neighbor["payload"]["api_name"]}'
                    if neighbor_node not in neighbors:
                        neighbors.append(neighbor_node)
                    if len(neighbors) >= 5:
                        break

            next_step = self.choose_neighbor(query, path, neighbors)
            if next_step:
                next_node = next_step.get("action", None)
                
            if next_node is None:
                print("选择的下一个节点无效，停止遍历。")
                break

            print(f"Next Node Selected: {next_node}")

            path.append(next_node)
            current_node = next_node
            visited_count += 1

        return path

    def choose_neighbor(self, query, path, neighbors):
        """
        根据当前路径和邻居节点，调用 LLM 选择下一个节点。
        
        :param path: List[str] - 当前已访问路径
        :param neighbors: List[str] - 可选择的邻居节点
        :return: str - 选择的下一个邻居节点
        """
        llm = get_qwen25_7b()
        prompt = f"""你是一个非常专业和睿智的计算机学生，你负责调用API工具来完成任务。
        
# 任务
{query} 

# 可选的工具
{"\n".join(neighbors)}

# 当前已经选择的工具（请勿重复选择）
{path}
        
# 指令
1. 你只能选我提供的API工具，并且只能选择1个
2. 请你选择尽可能少的API工具，如果已经选择的工具能完成，就在action输出end。
3. 但凡你认为当前选择的工具能够完成任务，请你以end作为action。
4. 在thought中用10-20个字简单描述你的思考，action部分填写API的名称。

# 输出格式
{{"thought":"", "action": "工具名称或者end"}}
        """
        print(prompt)
        ans = llm.invoke(prompt)
        plan = json.loads(ans)
        return plan

    def main(self, query: str):
        tool_sequences = self.parse_toolbench_file()
        G = self.build_graph_from_json(tool_sequences)
        print(f"No. of Graph Nodes: {len(G.nodes)}")
        decomposer = Decomposer("qwen2.5:7b", query)
        sub_tasks = decomposer.run()

        for sub_task in sub_tasks:
            print("=======================")
            print(sub_task)
            print("=======================")
            path = self.traverse_graph(G, f"{sub_task['name']}:{sub_task['description']}", sub_task['category'])
            print(f"Traversal Path: {path}")

if __name__ == "__main__":
    # 执行主程序
    traversal = GraphTraversal('./data/instruction/G1_query.json', './rapidapi_all_apis.json')
    traversal.main("what's the recipe of chicken soup?")