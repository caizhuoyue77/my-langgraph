from typing import Optional, List, Tuple
import json
from free_gpt import get_chat_response, count_tokens
from config import PROMPT_TEMPLATE as REWOO_PROMPT


def rewoo_func(query: str, api_list) -> Tuple[str, List[str]]:
    """
    生成 API 调用计划。

    参数:
    query (str): 用户查询
    api_list (List[str]): 可用的API列表

    返回:
    Tuple[str, List[str]]: 计划描述和API调用的列表
    """
    # 拼接所有的API为一个字符串
    api_string = str(api_list)
    
    # 调用模型生成计划
    prompt = REWOO_PROMPT.replace("{tool_list}", api_string)
    
    prompt = prompt.replace("{task}", query)
    
    plan = get_chat_response(prompt)
    
    # 解析计划（这里假设返回格式为字符串和API列表）
    # 具体解析根据模型返回的内容格式调整
    if plan:
        return plan, api_list  # 示例返回，需根据实际解析进行调整
    return "计划生成失败", []


def get_plan_for_dataset(dataset: List[str], api_list, make_plan_func: callable = rewoo_func):
    """
    为数据集中的所有查询生成计划并存储到文件。

    参数:
    dataset (List[str]): 查询列表
    api_list (List[str]): 可用的API列表
    make_plan_func (callable): 生成计划的函数
    """
    all_plans = []
    
    for query in dataset:
        plan, api_calls = make_plan_func(query, api_list)
        all_plans.append({
            "query": query,
            "plan": plan,
            "api_calls": api_calls
        })
    
    return all_plans
    

def baseline_1():
    # 示例基础实现
    pass

def baseline_2():
    # 示例基础实现
    pass