import time
from pass_rate import PassRate
from langchain_ollama import OllamaLLM

class ReAct:
    def __init__(self, model_name, tools, query, max_iter=4):
        """
        ReAct类的初始化函数
        :param model_name: 模型名称
        :param tools: 可用工具列表
        :param query: 用户查询任务
        :param max_iter: 最大迭代次数
        """
        self.tools = tools  # 工具列表
        self.model_name = model_name  # 模型名称
        self.max_iter = max_iter  # 最大迭代深度
        self.query = query  # 用户的查询任务
        self.llm = OllamaLLM(model=model_name)  # 使用Ollama模型
        self.scratch_pad = []  # 执行过程的记录
        self.final_plan = []  # 最终的计划路径
        self.execution_count = {}  # 记录每个API的调用次数
        self.final_answer = ""

    def call_api(self, prompt: str) -> str:
        """
        调用 LLM 接口获取回答
        :param prompt: 传递给 LLM 的提示信息
        :return: LLM 的响应结果
        """
        answer = self.llm.invoke(prompt)
        return answer

    def run(self) -> list:
        """
        启动深度优先搜索（DFS），并维护一个树状结构
        :return: 最终的规划和执行路径
        """
        # 以 DFS 方式启动搜索，初始深度为 0
        success = self._dfs(current_depth=0, current_scratch_pad=[])
        message = "找到满足条件的路径!" if success else "未能找到满足条件的路径。"
        print(message)
        return self.final_plan

    def _dfs(self, current_depth: int, current_scratch_pad: list) -> bool:
        """
        深度优先搜索递归函数
        :param current_depth: 当前递归深度
        :param current_scratch_pad: 当前路径中的执行步骤记录
        :return: 是否找到正确的路径
        """
        # 如果达到最大深度，停止搜索并回溯
        if current_depth >= self.max_iter:
            return False
        self.scratch_pad = current_scratch_pad 

        # 调用 choose 函数判断是否已经完成任务，并选择下一个API
        end, chosen_api = self.choose()
        if end:  # 如果模型认为任务已经完成，则保存最终结果并返回成功
            self.final_plan = current_scratch_pad[:]
            
            judge = PassRate(self.query, self.final_plan, self.tools, self.final_answer)
            pass_rate = judge.run()
            
            if pass_rate <= 0:
                print(f"深度 {current_depth}: 路径输出为end，但任务未完成，路径为: {self.final_plan}")
            else:
                # print(f"深度 {current_depth}: 任务已完成，路径为: {self.final_plan}")
                return True

        # 防止同一工具被反复调用，增加一个计数条件
        self.execution_count[chosen_api] = self.execution_count.get(chosen_api, 0) + 1

        # 如果某个工具被调用超过2次，则认为进入死循环，停止搜索并回溯
        if self.execution_count[chosen_api] > 2:
            print(f"警告: 工具 {chosen_api} 被多次调用，可能进入死循环，回溯中...")
            return False

        # 针对模型选择的API进行调用并记录结果
        if chosen_api in self.tools:
            # 调用选择的工具，并获取执行结果
            result = self.call_tool(chosen_api)

            # 记录当前操作到 scratch_pad 中
            current_scratch_pad.append({"action": chosen_api, "observation": f"反馈: {result}"})

            # 递归向深层探索
            if self._dfs(current_depth + 1, current_scratch_pad):
                return True  # 如果找到正确路径，返回成功

            # 回溯：移除当前操作
            print(f"深度 {current_depth}: 回溯, 移除工具 {chosen_api}")
            current_scratch_pad.pop()

        return False

    def is_finished(self) -> bool:
        prompt = f"""
请你判断，利用下列的工具调用路径和结果，是否能够解决问题。

当前任务:{self.query}

当前路径:{self.scratch_pad}

请输出continue或者end，continue表示未完成任务，end表示完成任务。
"""
        ans = self.llm.invoke(prompt)
        return "end" in ans.lower()

    def choose(self) -> tuple:
        """
        选择下一个工具或判断任务是否完成
        :return: 是否完成任务（end），以及模型选择的工具名称
        """
        prompt = f"""你好，请你帮我选择一组API来完成用户任务。
        
当前的任务：{self.query}。

备选的API：
{self._parse_tools()}。

当前已经执行的步骤和结果:{self._parse_scratch_pad()}。
        
你只能选择下一个工具，直接输出API名称。如果你认为已经完成任务，直接输出end即可。
        """
        ans = self.llm.invoke(prompt)
        end = "end" in ans.lower()  # 判断是否已经完成任务
        chosen_api = ans.strip().split("\n")[0]  # 选择的API或是“end”
        return end, chosen_api

    def call_tool(self, tool_name: str) -> str:
        """
        模拟调用工具并返回结果
        :param tool_name: 工具名称
        :return: 工具执行结果
        """
        return f"{tool_name} 成功执行，得到结果：天气晴朗，17-27度。"

    def _parse_tools(self) -> str:
        """
        解析可用工具列表为字符串格式
        :return: 解析后的工具列表字符串
        """
        return "\n".join(self.tools)

    def _parse_scratch_pad(self) -> str:
        """
        解析当前的执行记录为字符串格式
        :return: 解析后的执行记录字符串
        """
        scratch_pad_str = "\n".join([f"步骤 {i + 1}:\nAction: {item['action']}\nObservation: {item['observation']}"
                          for i, item in enumerate(self.scratch_pad)])
        return scratch_pad_str


# 扩充的工具库
TOOLS = [
    "根据地点查询经纬度", 
    "根据经纬度获得天气", 
    "计算器", 
    "谷歌搜索", 
    "货币汇率查询", 
    "文本翻译",
    "维基百科查询", 
    "新闻摘要生成", 
    "旅游推荐", 
    "航班状态查询", 
    "城市地铁查询", 
    "股票价格查询", 
    "美食推荐",
    "附近酒店查询"
]

# 测试代码
react = ReAct("qwen2.5:3b", TOOLS, "今天大阪的天气怎么样?")
ans = react.run()
print("执行路径:", ans)