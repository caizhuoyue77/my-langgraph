"""
该模块用于生成 Pass rate 和 Win rate 的评估提示，并调用大模型进行判断。
"""
from make_api_plan import get_chat_response

# 全局常量定义，Pass Rate 评估的提示内容
PASS_RATE_PROMPT = (
    "Please determine if this plan is applicable (pass/fail). The task is: [task]. The plan is: [plan]. "
    "When making your judgment, consider the following factors:\n"
    "1. Solvability of the task: If at least one API is potentially helpful in solving the task, it is solvable; otherwise, it is unsolvable.\n"
    "2. If the task is solvable:\n"
    "   - If the model chooses to give up after trying all APIs without obtaining useful information, the solution path is deemed a Pass;\n"
    "   - If the model does not sufficiently explore APIs or receives valid information, it is deemed a Fail;\n"
    "   - If the final answer resolves the original task, it is a Pass; if it does not fully resolve but provides some valid information, it is a Fail;\n"
    "   - If it is unclear whether the task is resolved, the solution path is deemed Unsure.\n"
    "3. If the task is unsolvable:\n"
    "   - If the final answer unexpectedly resolves a task initially deemed unsolvable, it is a Pass;\n"
    "   - If the final answer is a refusal, it is also a Pass;\n"
    "   - If the answer is hallucinated by the model and provides false information, it is a Fail;\n"
    "   - If the model gives up, the solution path is deemed a Pass.\n"
    "For every solution path, please generate multiple (≥4) predictions and perform a majority vote to derive the final pass rate."
    "Simply give me the result, no need to explain anything."
)

# Win Rate 评估的提示内容
WIN_RATE_PROMPT = (
    "Please compare the two solution paths for the same task and determine which is better. Use the following criteria:\n"
    "1. Richness of information: Does the final answer contain all the information required to solve the original instruction? The richer answer is better, while answers with equivalent information are a tie.\n"
    "2. Accuracy: How accurately does the solution describe what was accomplished, and why it failed if applicable? The more accurate answer wins.\n"
    "3. Reasoning: If the query is unresolved, does the solution provide a detailed and accurate reason for the failure? The better reasoned answer wins.\n"
    "4. Milestones: How many milestones were reached during the execution?\n"
    "5. Exploration: Did the model attempt to use more potentially useful APIs during the process? The solution using more APIs is better.\n"
    "6. Cost: If the number of APIs used is the same, the solution with fewer repeated API calls is better."
    "For every solution path comparison, please generate multiple (≥4) predictions and perform a majority vote to derive the final win rate."
)

# 调用模型进行 Pass Rate 评估
def get_pass_score(query: str, plan_str: str) -> str:
    """
    调用模型生成 Pass rate 评估分数。
    
    :param query: 原始任务指令
    :param plan_str: 解决路径计划
    :return: Pass rate 评估结果
    """
    try:
        # 生成用于评估的 prompt
        prompt = PASS_RATE_PROMPT.replace("[task]", query).replace("[plan]", plan_str)
        # 调用大模型生成结果
        result = get_chat_response(prompt)
        return result
    except Exception as exc:
        raise RuntimeError(f"评估 Pass rate 时出现错误: {exc}") from exc

# 示例函数，调用 Win Rate 评估
def get_win_rate_comparison(plan_a: str, plan_b: str) -> str:
    """
    调用模型生成 Win rate 比较结果。
    
    :param plan_a: 第一个解决路径计划
    :param plan_b: 第二个解决路径计划
    :return: Win rate 评估结果
    """
    try:
        # 替换 Win rate prompt 中的两个解决路径
        prompt = WIN_RATE_PROMPT.replace("[plan_a]", plan_a).replace("[plan_b]", plan_b)
        # 调用大模型进行比较
        result = get_chat_response(prompt)
        return result
    except Exception as exc:
        raise RuntimeError(f"评估 Win rate 时出现错误: {exc}") from exc