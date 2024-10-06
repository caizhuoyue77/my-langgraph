import time
import json
from api_retriever import APIRetriever
from langchain_ollama import OllamaLLM

class BasePlanner:
    """父类，包含公共属性和方法。"""
    def __init__(self, model_name: str, query: str, category: str, max_iter: int = 4):
        self.model_name = model_name
        self.max_iter = max_iter
        self.query = query
        self.llm = OllamaLLM(model="qwen2.5:7b")  # 初始化LLM模型
        self.scratch_pad = []  # 存储每一步的执行步骤和结果
        self.final_answer = []  # 存储最终答案
        self.final_plan = []  # 存储执行过的计划步骤
        self.category = category
        self.retriever = APIRetriever()
        self.long_term_memory = []
        self.tools = self.retriever.query_database(query, "api", self.category)  # 查询API工具集
    
    
    def run(self):
        index = 0
        while True and index < self.max_iter:
            plan = self.choose()
            
            thought = plan.get("thought", None)
            action = plan.get("action", None)
            
            if action.lower() == "end":
                break
            
            result = None
            index += 1
            result = self.call_tool(action)
                
            if result:
                self.final_plan.append(action)
                self.scratch_pad.append(plan)
                plan["observation"] = result
                
        return self.scratch_pad
    
    def call_tool(self, tool_name: str) -> str:
        """调用指定的工具并返回结果。"""
        return f"工具成功执行，得到结果 {tool_name}"

    def _parse_tools(self) -> str:
        """将工具列表格式化为字符串。"""
        return "\n".join([f"{tool['payload']['tool_name']}-{tool['payload']['api_name']}: {tool['payload']['api_description']}" for tool in self.tools])
    
    def _parse_scratch_pad(self) -> str:
        """将已经执行的步骤格式化为字符串。"""
        return "\n".join([f"{item['step']}: {item['result']}" for item in self.scratch_pad])
    
    def _parse_plan_str(self, plan_str):
        """Generate subtasks based on the provided query."""
        try:
            plan = json.loads(plan_str)
        except json.JSONDecodeError:
            print("JSON decode error: Returning an empty list.")
            plan = None

        return plan
    
    def build_prompt(self):
        return "hello"      
    
    def choose(self):
        ans = self.llm.invoke(self.build_prompt())
        print(ans)
        plan = self._parse_plan_str(ans)
        return plan
    
    def _all_tool_names(self):
        return [f"{tool['payload']['tool_name']}-{tool['payload']['api_name']}" for tool in self.tools]
        