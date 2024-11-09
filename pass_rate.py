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
        prompt = self._construct_simple_prompt()
        
        # print("PROMPT")
        # print(prompt)
        
        # 调用模型进行评判
        try:
            print("-----------------------")
            print(self.query)
            print("")
            print(self.plan)
            print("")
            ans = self.llm.invoke(prompt)
            print(ans)
            print("")
            ans = json.loads(ans)
            ans = ans.get("评判","失败")
            return self._interpret_result(ans)
        except Exception as exc:
            print(f"调用模型时发生错误: {exc}")
            return self.FAILURE  # 在发生错误时返回失败
            
            
    def _construct_simple_prompt(self):
        """构建评判提示的函数。"""
        return f"""
你是一个严格的评价者，我希望你帮助我评判对于一条用户指令，我们的系提供提供的解决路径是否可用。

# 前提
假设所有的用户指令都是可解的。

# 规则
3个等级：通过、失败、不确定。

- 如果提供的解决路径的API能够辅助完成任务，那么输出“通过”
- 如果提供的解决路径的API不能够辅助完成任务，那么输出“失败”
- 如果你不确定是否能完成任务，那么输出“不确定”

下面请你认真给出你的评判。注意：你需要给出结果和20字内的理由,具体到哪些任务未完成。

用户指令：{self.query}
解决工具调用路径：{self.plan}

# 格式（请你严格遵守下列格式)
{{"评判":"","理由":""}}

你的评判：
"""
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
# if __name__ == "__main__":
#     query = "请告诉我今天的天气。"
#     plan = "使用API获取天气信息。"
#     tools = "天气API"
#     final_answer = "天气晴朗，温度在20-25度之间。"
    
#     evaluator = PassRate(query, plan, tools, final_answer)
#     result = evaluator.run()
#     print(f"评判结果: {result}")  # 输出结果 1
    
import json

# 定义 PassRate 类（你已经有的部分，不需要重复提供）

def evaluate_and_save_pass_rate(input_jsonl_path: str, output_jsonl_path: str):
    """
    读取 JSONL 文件，对每条记录进行 PassRate 评价，并输出到新的 JSONL 文件中，附加 pass_rate 字段。
    
    :param input_jsonl_path: 输入 JSONL 文件路径
    :param output_jsonl_path: 输出 JSONL 文件路径
    """
    with open(input_jsonl_path, 'r', encoding='utf-8') as infile, open(output_jsonl_path, 'w', encoding='utf-8') as outfile:
        # 逐行读取 JSONL 数据
        for line in infile:
            # 解析 JSON 数据
            json_obj = json.loads(line.strip())
            
            # 获取评价所需的字段
            step = json_obj.get("step", {})
            action = step.get("action", "")
            result = json_obj.get("result", "")
            
            # 构造 query, plan, tools 和 final_answer (根据你的实际逻辑调整)
            query = json_obj.get("query", "")
            plan = json_obj.get("plan", "")
            tools = []
            final_answer = ""
            
            # 创建 PassRate 实例并计算 pass_rate
            evaluator = PassRate(query, plan, tools, final_answer)
            pass_rate = evaluator.run()
            
            # 将 pass_rate 添加到当前 JSON 对象
            json_obj['pass_rate'] = pass_rate
            
            # 将处理后的结果写入新的 JSONL 文件
            outfile.write(json.dumps(json_obj, ensure_ascii=False) + '\n')

    print(f"处理完成，带有 pass_rate 的数据已保存到: {output_jsonl_path}")

# 使用示例
if __name__ == "__main__":
    input_file = "ours@3_results_10.jsonl"  # 输入 JSONL 文件路径
    output_file = "ours@3_results_10_with_pr"  # 输出 JSONL 文件路径
    evaluate_and_save_pass_rate(input_file, output_file)