import time
import json
from api_retriever import APIRetriever
from langchain_ollama import OllamaLLM
import re

class BasePlanner:
    """父类，包含公共属性和方法。"""
    def __init__(self, model_name: str, query: str, category: str, max_iter: int = 3):
        self.model_name = model_name
        self.max_iter = max_iter
        self.query = query
        self.llm = OllamaLLM(model="qwen2.5:7b")  # 初始化LLM模型
        self.scratch_pad = []  # 存储每一步的执行步骤和结果
        self.final_answer = []  # 存储最终答案
        self.final_plan = []  # 存储执行过的计划步骤
        self.category = category
        self.temp_tool_dict = {}
        self.retriever = APIRetriever()
        self.long_term_memory = [] 
        self.all_tools = set([])
        self.tools = self.retriever.query_database(query, "api", self.category)  # 查询API工具集
    
    def get_tools(self):
        return self.tools
    
    def get_api_fullname(self, s):
        # 删除开头结尾的空格
        s = s.strip()
        # 将所有不是数字、字母、下划线的符号替换为下划线
        return re.sub(r'[^\w]+', '_', s.lower())

    def run(self):
        index = 0
        last_action = ""
        while True and index < self.max_iter:
            plan = self.choose()
            
            thought = plan.get("thought", None)
            action = plan.get("action", None)
            
            if action.lower() == "end":
                break
            
            if last_action == action:
                continue
            
            result = None
            index += 1
            result = self.call_tool(action)
                
            if result:
                self.final_plan.append(action)
                self.scratch_pad.append(plan)
                plan["observation"] = result
            
            last_action = action
                
        return self.scratch_pad
    
    def call_tool(self, tool_name: str) -> str:
        """调用指定的工具并返回结果。"""
        return f"工具成功执行，得到结果 {tool_name}"

    def _parse_tools(self) -> str:
        """将工具列表格式化为字符串并填充临时工具字典。"""
        
        result_list = []
        for tool in self.tools:
            # 获取完整的 API 名称            
            api_fullname = self.get_api_fullname(tool['payload']['api_name'] + " for " + tool['payload']['tool_name'])
            api_description = tool['payload']['api_description']
            
            self.all_tools.add(api_fullname)
            
            # 填充到临时字典
            self.temp_tool_dict[api_fullname] = api_description
            
            # 构建每一条工具的描述
            result_list.append(f"{api_fullname} description:{api_description}")
        
        # 返回拼接好的工具描述字符串
        return "\n\n".join(result_list)
    
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
    
    def get_all_tools(self):
        return self.all_tools 
    
    def choose(self):
        ans = self.llm.invoke(self.build_prompt())
        print(ans)
        plan = self._parse_plan_str(ans)
        return plan
    
    def get_plan(self):
        return self.final_plan
    
    def _get_api_description(self, full_name):
        return self.temp_tool_dict.get(full_name, "")
    
    def _all_tool_names(self):
        print("_all_tool_names"+ str(self.temp_tool_dict.keys()))
        return self.temp_tool_dict.keys()
        