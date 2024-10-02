import time

from langchain_ollama import OllamaLLM

class ReAct:
    def __init__(self, model_name, tools, query, max_iter = 4):
        self.tools = tools
        self.model_name = model_name
        self.max_iter = max_iter
        self.query = query
        self.llm = OllamaLLM(model="qwen2.5:3b")
        self.scratch_pad = []
        self.final_answer = []
        self.final_plan = []
        
    def call_api():
        prompt = "你好"
        
        answer = self.llm.invoke(prompt)
        
        return answer

    def run(self):
        index = 0
        while True and index < self.max_iter:
            end, planning = self.choose()
            
            result = None
            index += 1
            # if tool_name in self.tools:
            result = self.call_tool(planning)
            plannings = planning.split('\n')
            
            thought, action = "", ""
            
            if len(plannings) > 1:
                thought = plannings[0]
                action = plannings[1]
                
            if result:
                self.final_plan.append(action)
                self.scratch_pad.append({"thought": thought,"action": action, "observation": f"反馈:{result}"})
                
            if end:
                break
        
        return self.scratch_pad
          
    def choose(self):
        prompt = f"""你好，请你帮我选择一组API来完成用户任务。
        
当前的任务：{self.query}。

备选的API：
{self._parse_tools()}。
当前已经执行的步骤和结果:{self._parse_scratch_pad()}。
        
你只能选择下一个工具，直接输出API名称。如果你认为已经完成任务，直接输出end即可。

请遵守这个输出格式:(必须有thought和action):
thought:关于当前的已执行步骤和用户任务的思考，思考下一步怎么做。
action：工具名称，或者是end
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
        return "\n".join([f"步骤 {i + 1}:\nThought: {item['thought']}\nAction: {item['action']}\nObservation: {item['observation']}"
                      for i, item in enumerate(self.scratch_pad)])
        
react = ReAct("qwen2.5:3b", ["经纬度查询：地点名-》经纬度" , "根据经纬度获得天气", "计算器", "谷歌搜索"], "今天大阪的天气怎么样?")

ans = react.run()

print(ans)
