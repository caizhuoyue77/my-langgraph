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
        ans = self.llm.invoke(self.build_prompt(neighbors))
        plan = self._parse_plan_str(ans)
        if plan is None:
            return {"action": "Finish"}  # 或者其他默认值
        return plan
    
    def _parse_neighbor_tools(self, neighbors):
        """将工具列表格式化为字符串并填充临时工具字典。"""
        tool_strs = []
        if not neighbors:
            return "没有API了，请直接输出end结束"
        for item in neighbors.keys():
            tool_strs.append(f"{item} 权值：{neighbors[item]}")
        return "\n".join(tool_strs)
            
    def build_prompt(self, neighbors):
        # 根据邻居的“call”边数量进行加权选择
        
        if not neighbors:
            tools = self._parse_tools()
        else:
            tools = self._parse_neighbor_tools(neighbors)
        prompt = f"""你好，请你帮我选择一组API来完成用户任务。
        
当前的任务：{self.query}。

备选的API：
{tools}。

当前已经执行的步骤和结果
{self._parse_scratch_pad()}。
        
你只能选择下一个工具作为action，请直接输出API名称。
如果你认为已经完成任务，直接输出end即可。
"thought"部分只需要用10个字简单介绍选择理由。
"action"部分是选择的API的全名。或者是"end"。
如果你觉得所有API都不能帮助解决问题，也请你输出"end"。

请遵守这个输出格式:(必须有thought和action):
{{"thought":"","action":""}}
"""
        return prompt
        
        
    def run(self):
        """从随机选择的API节点开始，逐步选择路径
        """
        # 获取所有初始的API节点
        api_nodes = self.tools
        # print(f"初始API节点: {api_nodes}")
        
        if not api_nodes:
            print("没有找到API节点。")
            return

        # 随机选择一个API节点
        # 第一个节点也是去让llm选择
            
        current_plan = self.choose(None)
        
        if current_plan:
            current_node = current_plan.get("action", None)
        else:
            current_node = "Finish"
        print(f"当前的计划:{current_plan}")
        
        scratch_pad_plan = {"step": current_plan, "result":  f"成功调用{current_node}，获取到相关的信息"}
        self.scratch_pad.append(scratch_pad_plan)
        self.final_plan.append(current_node)

        # 开始选择路径
        while True and len(self.final_plan) < self.max_iter:
            neighbors = self.connector.find_neighbors(current_node)
            if not neighbors:
                print(f"{current_node} 没有邻居节点，结束选择。")
                # 用相似度搜索几个相似的api（根据当前的api和query）
                # 
            
            # 根据邻居选择下一个节点
            next_plan = self.choose(neighbors)
            if next_plan:
                next_node = next_plan.get("action", None)
            else:
                next_node = "Finish"
                
            scratch_pad_next_plan = {"step": next_plan, "result":  f"成功调用{next_node}，获取到相关的信息"}
            self.scratch_pad.append(scratch_pad_next_plan)
            self.final_plan.append(next_node)

            # 更新当前节点
            current_node = next_node
        print("芜湖～顺利结束啦～")
        return self.final_plan

# 使用示例
if __name__ == "__main__":
    selector = GraphSelector(model_name="", query="what's the weather like in CS", category="", max_iter=3)

    # 从随机API节点开始选择路径
    selector.run()
    
    print(f"最终路径:{selector.final_plan}")

    selector.connector.close()