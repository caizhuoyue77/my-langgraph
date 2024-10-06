import time
import logging
from base_planner import BasePlanner
from langchain_ollama import OllamaLLM


class Vanilla(BasePlanner):
    """
    Vanilla 是一个任务执行类，继承自 BasePlanner。
    该类负责通过 LLM 模型根据用户查询选择合适的 API 工具，并按步骤执行任务。
    """


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
                        
            if action in self._all_tool_names():
                result = self.call_tool(action)
                if result:
                    self.final_plan.append(action)
                    self.scratch_pad.append({"step":plan, "result": result})
        
        print(self.scratch_pad)
        return self.scratch_pad

    def build_prompt(self):

        prompt = f"""你好，请你帮我选择一组API来完成用户任务。
        
当前的任务：{self.query}。

备选的API：
{self._parse_tools()}。
当前已经执行的步骤和结果:{self._parse_scratch_pad()}。
        
你只能选择下一个工具作为action，请直接输出API名称。如果你认为已经完成任务，直接输出end即可。

请遵守这个输出格式:(只需要action):
{{"action":""}}"""
        
        return prompt

    def call_tool(self, tool_name: str) -> str:
        """
        调用指定的 API 工具并返回执行结果。
        
        :param tool_name: 需要调用的工具名称。
        :return: 工具调用结果（字符串）。
        """
        print(f"调用工具 {tool_name} 中...")
        result = f"工具 {tool_name} 成功执行，得到结果"
        print(f"调用成功，返回结果: {result}")
        return result
