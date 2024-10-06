import time
from langchain_ollama import OllamaLLM
from base_planner import BasePlanner
from api_retriever import APIRetriever

class ReAct(BasePlanner):

    def run(self):
        index = 0
        while True and index < self.max_iter:
            plan = self.choose()
            if plan:
                thought = plan.get("thought", None)
                action = plan.get("action", None)
            
            if action == "end":
                break
            
            result = None
            index += 1
            result = self.call_tool(action)
                
            if result:
                self.final_plan.append(action)
                plan["observation"] = result
                self.scratch_pad.append({"step": plan, "result": result})
        
        return self.scratch_pad
          
    def choose(self):    
        """
        Solve a question answering task with interleaving thought, Action, Observation steps. thought can reason about the current situation, and Action can be three types: 
        (1) Search[entity], which searches the exact entity on Wikipedia and returns the first paragraph if it exists. If not, it will return some similar entities to search.
        (2) Lookup[keyword], which returns the next sentence containing keyword in the last passage successfully found by Search.
        (3) Finish[answer], which returns the answer and finishes the task.
        You may take as many steps as necessary.
        Here are some examples:
        {examples}
        (END OF EXAMPLES)
        Question: {question}{scratchpad}
        """
        prompt = f"""你好，请你帮我选择一组API来完成用户任务。
        
当前的任务：{self.query}。

备选的API：
{self._parse_tools()}。
当前已经执行的步骤和结果:{self._parse_scratch_pad()}。
        
你只能选择下一个工具作为Action，请直接输出API名称。如果你认为已经完成任务，直接输出end即可。

请遵守这个输出格式:(必须有thought和action):
{{"thought":"","action":""}}
"""
        ans = self.llm.invoke(prompt)
        print(f"ANS:{ans}")
        plan = self._parse_plan_str(ans)
        print(f"PLAN:{plan}")
        return plan
    
    def _parse_scratch_pad(self):
        return "\n".join([f"步骤 {i + 1}:\nThought: {item['thought']}\nAction: {item['action']}\nObservation: {item['observation']}"
                      for i, item in enumerate(self.scratch_pad)])