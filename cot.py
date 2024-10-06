import time

from qwen25_7b import get_qwen25_7b
from base_planner import BasePlanner
from api_retriever import APIRetriever

class COT(BasePlanner):

    def run(self):
        index = 0
        while True and index < self.max_iter:
            plan = self.choose()
            if plan:
                action = plan.get("Action", None)
            else:
                action = None
            
            print(plan)
            print(self._all_tool_names())
            if action == "end":
                break
                
            result = None
            index += 1
                        
            if action in self._all_tool_names():
                result = self.call_tool(action)
                print("添加一个工具")
                if result:
                    self.final_plan.append(action)
                    self.scratch_pad.append({"step":plan, "result": result})
        
        return self.scratch_pad
          
    def choose(self):
        """
        Solve a question answering task by having a thought, then Finish with your answer.
        thought can reason about the current situation. Finish[answer] returns the answer and finishes the task.

        You will be given context that you should use to help you answer the question.

        Here are some examples:
        {examples}
        (END OF EXAMPLES)
        {reflections}
        Relevant Context: {context} 
        Question: {question}{scratchpad}
        """
        prompt = f"""
        
你好，请你帮我选择一组api来完成用户任务。

任务：{self.query}。

备选的API：
{self._parse_tools()}。

当前已经执行的步骤和结果:{self._parse_scratch_pad()}。

你只能选择下一个工具（每次选1个），直接输出API名称。如果你认为已经完成任务，直接输出end即可。

Let's think step by step. Give your reasoning process first, and then answer the question in a new line directly with no extra words.

# 格式
{{"Reasoning":"","Action":""}}  
"""
        print(prompt)
        print("")
        ans = self.llm.invoke(prompt)
        
        print(f"模型的回答:{ans}")
        plan = self._parse_plan_str(ans)
        
        return plan
        
    def call_tool(self, tool_name):
        return "工具成功执行，得到结果" 
    
    
    def _parse_scratch_pad(self):
        return "\n".join([f"{item['step']}: {item['result']}" for item in self.scratch_pad])