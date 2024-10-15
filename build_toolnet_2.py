"""
GraphSelector类用于从Neo4j图谱中随机选择节点，并通过邻居节点进行迭代选择。
"""

import random
from base_planner import BasePlanner

from neo4j_connector import Neo4jConnector  # 从其他文件导入Neo4jConnector

class GraphSelector(BasePlanner):
    def __init__(self, model_name, query, category, max_iter):
        """初始化图选择器
        :param connector: Neo4jConnector实例
        """
        super().__init__(model_name, query, category, max_iter)
        
        neo4j_uri = "bolt://localhost:7687"
        neo4j_user = "neo4j"
        neo4j_password = "daffodil"
        connector = Neo4jConnector(neo4j_uri, neo4j_user, neo4j_password)
        self.connector = connector
        
    def choose(self, neighbors: dict) -> str:
        """根据邻居节点的相关性选择下一个节点
        :param neighbors: 邻居节点字典
        :return: 选择的邻居节点名称
        """
        if not neighbors:
            return None
        # 根据邻居的“call”边数量进行加权选择
        total_calls = sum(neighbors.values())
        weights = [count / total_calls for count in neighbors.values()]
        return random.choices(list(neighbors.keys()), weights=weights, k=1)[0]

    def run(self):
        """从随机选择的API节点开始，逐步选择路径
        """
        # 获取所有API节点
        api_nodes = self.connector.get_all_api_nodes()
        if not api_nodes:
            print("没有找到API节点。")
            return

        # 随机选择一个API节点
        current_node = random.choice(api_nodes)
        print(f"起始节点: {current_node}")

        # 开始选择路径
        while True and len(self.final_plan) < self.max_iter:
            neighbors = self.connector.find_neighbors(current_node)
            if not neighbors:
                print(f"{current_node} 没有邻居节点，结束选择。")
                break
            
            # 根据邻居选择下一个节点
            next_node = self.choose(neighbors)
            self.final_plan.append(next_node)
            print(f"选择的下一个节点: {next_node}（'call'边数量: {neighbors[next_node]}）")

            # 更新当前节点
            current_node = next_node

# 使用示例
if __name__ == "__main__":
    selector = GraphSelector(model_name="", query="what's the weather like in CS", category="", max_iter=3)

    # 从随机API节点开始选择路径
    selector.run()
    
    print(f"最终路径:{selector.final_plan}")

    selector.connector.close()