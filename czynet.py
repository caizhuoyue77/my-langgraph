"""
CzyNet 类用于解析JSON文件、构建工具图谱，并进行图遍历。
"""

import json
import networkx as nx
import random
from collections import defaultdict
import copy
from api_retriever import APIRetriever
from qwen25_7b import get_qwen25_7b
from task_decomposer import Decomposer


class CzyNet:
    """
    该类实现了工具调用顺序的解析、图结构的构建以及基于图的随机遍历。
    """

    def __init__(self,json_file_path='./data/instruction/G1_query.json', 
                 tool_info_path='./rapidapi_all_apis.json'
                 ):
        """
        初始化CzyNet类。
        
        :param json_file_path: str - 工具调用的JSON文件路径
        :param tool_info_path: str - 工具信息的JSON文件路径
        """
        self.json_file_path = json_file_path
        self.tool_info_path = tool_info_path
        self.path = []
        self.api_dict = self._load_api_list()
        self.scratch_pad = []
        self.retriever = APIRetriever()
        self.G = None
        self.build_graph_from_json()

    def parse_toolbench_file(self) -> list:
        """
        解析JSON文件，提取relevant APIs字段。
        
        :return: List[List[Tuple]] - 返回工具调用序列的列表
        """
        tool_sequences = []

        # 读取JSON文件
        with open(self.json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 遍历每个查询，提取relevant APIs
        for entry in data:
            relevant_apis = entry['relevant APIs']
            tool_sequence = relevant_apis
            tool_sequences.append(tool_sequence)

        return tool_sequences

    def build_graph_from_json(self, api_info_file: str = None) -> nx.Graph:
        """
        构建基于工具调用顺序的静态图谱，并添加start和end节点。

        :param api_info_file: str - 如果不提供路径，则使用类成员变量self.tool_info_path
        :return: Graph - 构建的无向图
        """
        G = nx.Graph()
        transition_counts = defaultdict(int)  # 记录工具之间的转换次数

        tool_sequences = self.parse_toolbench_file()  # 获取工具调用序列

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

        # 如果未提供api_info_file，则使用类的默认路径
        if api_info_file is None:
            api_info_file = self.tool_info_path

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

        self.G = G_copy
        return G_copy

    def get_tool_info(self, tool_name: str) -> dict:
        """
        根据工具名称，在给定的工具信息JSON文件中查找详细描述。
        
        :param tool_name: str - 工具的名称
        :return: Dict - 工具的详细信息
        """
        # 读取工具信息文件
        with open(self.tool_info_path, 'r', encoding='utf-8') as file:
            tool_info_data = json.load(file)

        # 查找工具的详细描述
        for tool in tool_info_data:
            if tool.get('api_name') == tool_name:
                return tool

        return {}
    
    def call_tool(self, tool_name = ""):
        return f"{tool_name}正常执行，得到相应的结果"
        

    def run(self, query: str, category: str) -> list:
        """
        随机遍历图中的节点，直到到达end节点或访问节点数超过20。

        :param query: str - 查询字符串
        :param category: str - 工具类别
        :return: List[str] - 访问的节点路径
        """
        if self.G is None:
            print("Graph not built. Please run `build_graph_from_json` first.")
            return []

        # 通过检索器获取初始节点
        nodes = self.retriever.query_database(query, "api", category)
        
        if not nodes:
            print("No nodes found for the given query.")
            return []
        
        # 格式化初始节点信息，并编号
        neighbors, neighbor_names = self._parse_neighbors(nodes)

        print(f"Initial Neighbors: {neighbors}")

        # 调用 LLM 选择初始节点
        current_plan = self.choose_neighbor(query, [], neighbors)
        if current_plan:
            current_node = current_plan.get("action", None)
            current_thought = current_plan.get("thought", None)

        # 检查初始节点是否有效
        if not current_node or current_node not in neighbor_names:
            print(f"The starting node:{current_node} is not valid.")
            return []

        print(f"Starting Node: {current_node}")
        
        current_plan['result'] = self.call_tool(current_node)
        tool_name, api_name = current_node.split('-')[0], current_node.split('-')[1]
        current_plan['api_description'] = self._get_api_description(tool_name=tool_name, api_name=api_name)
        self.path.append(current_node)
        self.scratch_pad.append(current_plan)
        
        path = self._parse_path([], current_node, current_thought)  # 初始化路径
        visited_count = 0  # 已访问节点数

        # 随机遍历节点直到到达'end'或访问节点数超过限制
        while current_node != "end" and visited_count < 20:
            # print(f"Current Node: {current_node}")

            tool_name = current_node.split('-')[1] if '-' in current_node else current_node
            tool_info = self.get_tool_info(tool_name)
            # print(f"Tool Info for {tool_name}: {tool_info}")

            # 查找并美化所有邻居节点
            neighbor_str, neighbors = self._get_filtered_neighbors(current_node)
            
            if current_node in neighbors:
                neighbors.remove(current_node)
            
            # 选择下一个节点
            next_plan = self.choose_neighbor(query, path, neighbor_str)
            if next_plan:
                next_node = next_plan.get("action", None)
                next_thought = next_plan.get("thought", None)
                
            # print(f"NEIGHTBORS:{neighbors}")
            
            if next_node == "end":
                print("任务完成，结束循环")
                break

            if next_node is None or next_node not in neighbors:
                print(f"选择的下一个节点{next_node}无效，停止遍历。")
                break

            print(f"Next Node Selected: {next_node}")

            # 更新路径和当前节点
            if next_node != current_node:
                self.path.append(next_node)
                tool_name, api_name  = next_node.split('-')[0], next_node.split('-')[1]
                next_plan['api_description'] = self._get_api_description(tool_name=tool_name, api_name=api_name)
                next_plan['result'] = self.call_tool(next_node)
                self.scratch_pad.append(next_plan)
            current_node = next_node
            visited_count += 1

        return path
    
    
    def _parse_neighbors(self, nodes: list) -> tuple:
        """
        格式化输入的nodes列表，返回字符串和一个工具名称与API名称组合的列表。

        :param nodes: 输入的节点列表，每个节点是一个字典，包含'id'、'score'和'payload'。
        :return: 一个元组 (格式化字符串, 工具名称与API名称组合的列表)
        """
        # 定义用于存储字符串的列表
        formatted_string_list = []

        # 定义用于存储 "tool_name-api_name" 格式的列表
        output_list = []

        # 遍历每个节点，提取相应信息
        for index, node in enumerate(nodes):
            payload = node.get('payload', {})  # 获取payload字典
            api_name = payload.get('api_name', 'Unknown')
            tool_name = payload.get('tool_name', 'Unknown')
            api_description = payload.get('api_description', 'No description')

            # 将格式化后的字符串加入到列表中
            formatted_string_list.append(f"[{index + 1}]{tool_name}-{api_name}\ndescription: {api_description}")

            # 将"tool_name-api_name"格式添加到output_list
            tool_name = payload.get('tool_name', 'Unknown Tool')
            output_list.append(f"{tool_name}-{api_name}")

        # 将格式化字符串列表合并为单一字符串，并返回元组
        formatted_string = "\n".join(formatted_string_list)
        return formatted_string, output_list


    def _parse_path(self, path: list, node: str, thought: str) -> list:
        """
        美化路径记录，包含当前节点、选择原因及节点详细描述。

        :param path: List - 之前访问过的节点路径
        :param node: str - 当前节点
        :param thought: str - 节点选择的理由
        :return: List[str] - 美化后的路径列表
        """
        # 生成详细路径信息
        path_entry = {"thought" : thought, "action": node}  # 将选择理由加入路径
        path.append(path_entry)  # 将当前节点信息添加到路径中
        
        # 返回格式化后的路径列表，包含索引
        return [f"[{idx}] {tool}" for idx, tool in enumerate(path)]


    def _get_filtered_neighbors(self, current_node: str) -> tuple:
        """
        过滤当前节点的邻居，排除无效节点（start和end）。

        :param current_node: str - 当前节点名称
        :return: tuple - (有效邻居的详细信息字符串, 有效邻居节点名称列表)
        """
        # 查找所有邻居（权重大于1，排除 start 和 end）
        neighbors = [
            neighbor for neighbor in self.G.neighbors(current_node)
            if self.G[current_node][neighbor].get('weight', 0) >= 1 and neighbor not in ["start", "end"]
        ]
        
        # 限制邻居数量最多为5
        if len(neighbors) > 5:
            neighbors = random.sample(neighbors, 5)

        # 补充邻居数量不足的情况（再从数据库检索新节点）
        elif len(neighbors) < 5:
            new_neighbors = self.retriever.query_database(current_node, "api")
            for new_neighbor in new_neighbors:
                neighbor_node = f'{new_neighbor["payload"]["tool_name"]}-{new_neighbor["payload"]["api_name"]}'
                
                if neighbor_node not in neighbors:
                    neighbors.append(neighbor_node)
                if len(neighbors) >= 5:
                    break
                
        
        # 创建字符串格式的邻居信息
        # 将每个邻居对象的信息格式化为字符串
        formatted_neighbors = []
        for index, neighbor in enumerate(neighbors):
            # print(neighbor)
            api_name = neighbor.split('-')[1]
            tool_name = neighbor.split('-')[0]
            description = self._get_api_description(api_name, tool_name)
            
            # 构建格式化的字符串
            formatted_neighbor = f"[{index + 1}] {neighbor}\nDescription: {description}"
            formatted_neighbors.append(formatted_neighbor)

        # 将所有邻居的描述信息连接为一个字符串，并以换行符分隔
        formatted_string = "\n".join(formatted_neighbors)
        
        return formatted_string, neighbors

    def _load_api_list(self, file_path: str = "rapidapi_all_apis.json") -> dict:
        """
        读取并加载JSON文件内容，并将数据转换为字典格式以提高查找效率。
        
        参数:
        - file_path (str): JSON文件的路径。
        
        返回:
        - dict: 将API信息转换为字典格式，键为(api_name, tool_name)，值为api_description。
        
        异常:
        - FileNotFoundError: 如果文件未找到。
        - json.JSONDecodeError: 如果文件不是有效的JSON格式。
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(f"成功加载文件: {file_path}")

                # 将API列表转换为字典，以便更快查找
                api_dict = {(api['api_name'], api['tool_name']): api['api_description'] for api in data}
                print("成功将API列表转换为字典格式！")
                return api_dict
        except FileNotFoundError as exc:
            print(f"文件未找到: {file_path}")
            raise FileNotFoundError(f"文件未找到: {file_path}") from exc
        except json.JSONDecodeError as exc:
            print(f"JSON格式错误: {file_path}")
            raise ValueError(f"JSON格式错误: {file_path}") from exc

    def _get_api_description(self, tool_name: str, api_name: str) -> str:
        """
        根据api_name和tool_name查找对应的api_description。
        
        参数:
        - api_dict (dict): 经过预处理的API字典，键为(api_name, tool_name)，值为api_description。
        - api_name (str): 要查找的API名称。
        - tool_name (str): 要查找的工具名称。
        
        返回:
        - str: 查找到的API描述信息，若未找到则返回提示信息。
        """
        return self.api_dict.get((api_name, tool_name), f"未找到api_name为'{api_name}'且tool_name为'{tool_name}'的API描述信息。")
            
        
    def choose_neighbor(self, query, path, neighbors):
        """
        根据当前路径和邻居节点，调用 LLM 选择下一个节点。
        
        :param path: List[str] - 当前已访问路径
        :param neighbors: List[str] - 可选择的邻居节点
        :return: str - 选择的下一个邻居节点
        """
        llm = get_qwen25_7b()
        
        prompt = f"""
Solve this task using the following tools.

# Task description/ Query description
{query}

# Tools
{neighbors}

# Currently selected tools
{path}

# Instructions
1. What OTHER tools should you use to do the task.
2. If the current selected tools are enough to do this task, you should simply use "end" as the action to finish the task.
3. For "thought", give brief reason. For "action", use a tool name or "end".
4. You should use the tool's fullname, with the '-'.

# Output format
{{"thought":"You reasons, less than 20 words","action":"some API's name"}}
"""
        max_attempts = 3  # 最大尝试次数
        for attempt in range(max_attempts):
            try:
                ans = llm.invoke(prompt)  # 调用 LLM
                import json
                plan = json.loads(ans)  # 解析 JSON 字符串
                return plan  # 返回解析后的计划
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e} - 尝试次数: {attempt + 1}")  # 捕获 JSON 解析错误
                if attempt < max_attempts - 1:
                    print("重新调用 LLM...")  # 继续尝试
                else:
                    print("已达到最大尝试次数，返回空字典。")
            except Exception as e:
                print(f"调用 LLM 时发生错误: {e}")  # 捕获其他错误
                return {}  # 返回空字典或适当的错误处理

        return {}  # 如果所有尝试都失败，返回空字典


# 运行示例
def main():
    czynet = CzyNet()
    czynet.build_graph_from_json()
    traversal_path = czynet.run("what's the weather in Bangkok", "weather")
    print(f"Final Path: {traversal_path}")


if __name__ == "__main__":
    main()