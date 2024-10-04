import time

from langchain_ollama import OllamaLLM
from pass_rate import PassRate

class Reflexion:
    def __init__(self, model_name, tools, query, max_iter = 4):
        self.tools = tools
        self.model_name = model_name
        self.max_iter = max_iter
        self.query = query
        self.llm = OllamaLLM(model="qwen2.5:7b")
        self.scratch_pad = [] # short term memory
        self.final_answer = []
        self.final_plan = []
        self.long_term_memory = []

    def run(self):
        index = 0
        while True and index < self.max_iter:
            end, tool_name = self.choose()
            
            if end:
                break
            result = None
            index += 1
            
            result = self.call_tool(tool_name)
            if result:
                self.final_plan.append(tool_name)
                self.scratch_pad.append({"step":f"Call tool:{tool_name}", "result": result})
            print(f"Scratch pad: {self._parse_scratch_pad()}")
        
        judge = PassRate(self.query, self.final_plan, self.tools, self.final_answer)
        pass_rate = judge.run()
        
        feedback = None
        if pass_rate <= 0:
            feedback = self.reflect()
            if feedback:
                print("反思")
                print(feedback)
                
        return feedback, self.scratch_pad
    
    def _reset(self):
        self.plan = []
        self.scratch_pad = []
        return
    
    def reflect(self):
        # 对当前的任务进行反思
        print("开始反思")
        
        prompt = f"""你好，我正在针对{self.query}进行工具执行顺序的规划。

当前的步骤和结果:{self._parse_scratch_pad()}

请你针对这个进行一些简短的思考和反馈。告诉我这个API调用链哪里做错了、哪里可以改进等。不需要提供代码，只需要针对API调用流程进行改进。

# 格式(注意分点)
1. ...
2. ...

现在开始你的分析："""
        
        ans = self.llm.invoke(prompt)
        
        print(f"模型的反思:{ans}")
        
        self.long_term_memory.append({"plan": self.final_plan, "feedback": ans})
        
        self._reset()
        
        return ans
        
          
    def choose(self):
        prompt = f"""
你好，请你帮我选择一组api来完成用户任务。任务：{self.query}。

备选的API：{self._parse_tools()}。

当前已经执行的步骤和结果:{self._parse_scratch_pad()}。

你只能选择下一个工具，直接输出API名称。如果你认为已经完成任务，直接输出end即可。

# 之前的历史尝试和反思
{self._parse_long_term_memory()}

注意，完成任务可以直接输出end来结束。
"""

        ans = self.llm.invoke(prompt)
        
        end = False
        if "end" in ans:
            end = True
    
        return end, ans
        
    def call_tool(self, tool_name):
        return "工具成功执行，得到结果" 
        
    def _parse_tools(self):
        return "\n".join(self.tools)
    
    def _parse_scratch_pad(self):
        return "\n".join([f"步骤 {i + 1}:工具: {item['step']}\n执行结果: {item['result']}"
            for i, item in enumerate(self.scratch_pad)])
        
    def _parse_long_term_memory(self):
        return "\n".join([f"步骤 {i + 1}:工具: {item['plan']}\n执行结果: {item['feedback']}"
            for i, item in enumerate(self.long_term_memory)])
    
reflexion = Reflexion("qwen2.5:3b", ["经纬度查询：地点名-》经纬度" , "根据经纬度获得天气", "计算器", "谷歌搜索"], "今天大阪的天气怎么样?")

feed_back, ans = reflexion.run()

if feed_back:
    print(reflexion.long_term_memory)

print(ans)
