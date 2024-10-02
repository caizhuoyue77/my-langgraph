import time

from qwen25_7b import get_qwen25_7b

class COT:
    def __init__(self, model_name, tools, query, max_iter = 4):
        self.tools = tools
        self.model_name = model_name
        self.max_iter = max_iter
        self.query = query
        self.llm = get_qwen25_7b()
        self.scratch_pad = []
        self.final_answer = []
        self.final_plan = []

    def run(self):
        index = 0
        while True and index < self.max_iter:
            end, planning = self.choose()
            
            if end:
                break
            
            tool_name = planning.split('\n')[-1].strip().split(':')[-1]
            
            print(f"tool_name:{tool_name}")
            
            result = None
            index += 1
            
            if tool_name in self.tools:
                result = self.call_tool(tool_name)
                if result:
                    self.final_plan.append(tool_name)
                    self.scratch_pad.append({"step":f"Call tool:{tool_name}", "result": result})
        
        return self.scratch_pad
          
    def choose(self):
        prompt = f"""
        
你好，请你帮我选择一组api来完成用户任务。

任务：{self.query}。

备选的API：
{self._parse_tools()}。

当前已经执行的步骤和结果:{self._parse_scratch_pad()}。

你只能选择下一个工具（每次选1个），直接输出API名称。如果你认为已经完成任务，直接输出end即可。

Let's think step by step. Give your reasoning process first, and then answer the question in a new line directly with no extra words.

选择工具：                  
"""
        
        ans = self.llm.invoke(prompt)
        
        end = False
        if "end" in ans:
            end = True
        
        print(f"模型的输出:{ans}")
        return end, ans
        
    def call_tool(self, tool_name):
        return "工具成功执行，得到结果" 
        
    def _parse_tools(self):
        return "\n".join(self.tools)
    
    def _parse_scratch_pad(self):
        return "\n".join([f"{item['step']}: {item['result']}" for item in self.scratch_pad])
    
    
vanilla = COT("qwen2.5:3b", ["经纬度查询：地点名-》经纬度" , "根据经纬度获得天气", "计算器", "谷歌搜索"], "今天大阪的天气怎么样?")

ans = vanilla.run()

print(ans)
