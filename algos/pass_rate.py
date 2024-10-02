import time

from langchain_ollama import OllamaLLM

from qwen25_7b import get_qwen25_7b


class PassRate:
    def __init__(self, query, plan, tools, final_answer):
        self.llm = get_qwen25_7b()
        self.query = query
        self.plan = plan
        self.tools = tools
        self.final_answer = "放弃，无法解决问题。"
        
    def run(self):
        prompt = f"""
你是一个严格的评价者，我希望你帮助我评判对于一条用户指令，我们的系提供提供的解决路径是否可用。

# 前提
假设所有的用户指令都是可解的。

# 规则
3个等级：通过、失败、不确定。

1. 如果模型给出的完成类型为“放弃”：
   - (a) 如果模型在调用了所有API并未获得有效信息，解决路径被视为通过。
   - (b) 如果模型仅调用了少量API或获取了有效信息但未解决问题，解决路径被视为失败。

2. 如果模型给出的完成类型为“最终答案”：
   - (a) 如果API未提供有效信息，且模型尝试了所有API仍未解决指令或表明无法提供帮助（如“抱歉，我无法提供帮助，因为工具不可用”），解决路径被视为通过。
   - (b) 如果工具提供了有效信息，但最终答案未完全解决指令或为拒绝答复，解决路径被视为失败。
   - (c) 如果最终答案完全解决了原始指令，解决路径被视为通过。
   - (d) 如果根据最终答案无法判断指令是否被解决，解决路径被视为不确定。

下面请你认真给出你的评判。注意：你只需要给评判结果，不需要给理由。

用户指令：{self.query}
工具列表：{self.tools}
解决路径：{self.plan}
最终回答：{self.final_answer}

你的评判："""

        
        # ans = self.llm.invoke(prompt)
        
        return ans