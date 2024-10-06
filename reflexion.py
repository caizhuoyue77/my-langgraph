import time

from langchain_ollama import OllamaLLM
from pass_rate import PassRate
from base_planner import BasePlanner


class Reflexion(BasePlanner):
    def __init__(self, model_name, query, category, max_iter = 4):
        self.model_name = model_name
        self.max_iter = max_iter
        self.query = query
        self.llm = OllamaLLM(model="qwen2.5:7b")
        self.scratch_pad = [] # short term memory
        self.final_answer = []
        self.final_plan = []
        self.long_term_memory = []
        self.category = category
        self.retriever = APIRetriever()
        self.tools = self.retriever.query_database(query, "api", self.category)


    def run(self):
        index = 0
        while True and index < self.max_iter:
            plan = self.choose()
            if plan:
                action = plan.get("action", None)
            else:
                action = None
            
            if action == "end":
                break
            
            result = None
            index += 1
            
            result = self.call_tool(action)
            
            if result:
                self.final_plan.append(action)
                self.scratch_pad.append({"step":plan, "result": result})
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
        """ 
        REFLECT_INSTRUCTION
        
        You are an advanced reasoning agent that can improve based on self refection. You will be given a previous reasoning trial in which you were given access to an Docstore API environment and a question to answer. You were unsuccessful in answering the question either because you guessed the wrong answer with Finish[<answer>], or you used up your set number of reasoning steps. In a few sentences, Diagnose a possible reason for failure and devise a new, concise, high level plan that aims to mitigate the same failure. Use complete sentences.  
        Here are some examples:
        {examples}

        Previous trial:
        Question: {question}{scratchpad}

        Reflection:
        """
        
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
        """
        REACT_REFLECT_INSTRUCTION = Solve a question answering task with interleaving Thought, Action, Observation steps. Thought can reason about the current situation, and Action can be three types: 
        (1) Search[entity], which searches the exact entity on Wikipedia and returns the first paragraph if it exists. If not, it will return some similar entities to search.
        (2) Lookup[keyword], which returns the next sentence containing keyword in the last passage successfully found by Search.
        (3) Finish[answer], which returns the answer and finishes the task.
        You may take as many steps as necessary.
        Here are some examples:
        {examples}
        (END OF EXAMPLES)

        {reflections}

        Question: {question}{scratchpad}
        """
        
        prompt = f"""
你好，请你帮我选择一组api来完成用户任务。任务：{self.query}。

备选的API：{self._parse_tools()}。

当前已经执行的步骤和结果:{self._parse_scratch_pad()}。

你只能选择下一个工具，直接输出API名称。如果你认为已经完成任务，直接输出end即可。

# 之前的历史尝试和反思
{self._parse_long_term_memory()}

注意，完成任务可以直接输出end来结束。

# 格式
{{"Thouhgt":"","Action:""}}
"""

        ans = self.llm.invoke(prompt)
        plan = self._parse_plan_str(ans)
        return plan
        
    def _parse_scratch_pad(self):
        return "\n".join([f"步骤 {i + 1}:工具: {item['step']}\n执行结果: {item['result']}"
            for i, item in enumerate(self.scratch_pad)])
        
    def _parse_long_term_memory(self):
        return "\n".join([f"步骤 {i + 1}:工具: {item['plan']}\n执行结果: {item['feedback']}"
            for i, item in enumerate(self.long_term_memory)])