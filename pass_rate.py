import time
from langchain_ollama import OllamaLLM
from qwen25_7b import get_qwen25_7b


class PassRate:
    # 定义常量
    SUCCESS = 1
    FAILURE = 0
    UNDETERMINED = -1
    
    def __init__(self, query, plan, tools, final_answer):
        self.llm = get_qwen25_7b()  # 获取LLM实例
        self.query = query
        self.plan = plan
        self.tools = tools
        self.final_answer = final_answer  # 接受用户最终回答
        
    def run(self):
        # 构建提示
        prompt = self._construct_prompt()
        
        # 调用模型进行评判
        try:
            return 1
            ans = self.llm.invoke(prompt)
            return self._interpret_result(ans)
        except Exception as exc:
            print(f"调用模型时发生错误: {exc}")
            return self.FAILURE  # 在发生错误时返回失败
            
    def _construct_prompt(self):
        """构建评判提示的函数。"""
        return f"""
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

你的评判：
"""

    def _interpret_result(self, result: str) -> int:
        """将模型结果解释为整数值。"""
        result = result.strip()  # 去除首尾空格
        if result == "通过":
            return self.SUCCESS
        elif result == "失败":
            return self.FAILURE
        elif result == "不确定":
            return self.UNDETERMINED
        else:
            print(f"未知结果: {result}")
            return self.UNDETERMINED  # 如果结果不在预期范围内，返回不确定


# 示例用法
if __name__ == "__main__":
    query = "请告诉我今天的天气。"
    plan = "使用API获取天气信息。"
    tools = "天气API"
    final_answer = "天气晴朗，温度在20-25度之间。"
    
    evaluator = PassRate(query, plan, tools, final_answer)
    result = evaluator.run()
    print(f"评判结果: {result}")  # 输出结果 1