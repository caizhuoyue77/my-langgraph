import os
import re
from typing import TypedDict, List
from config import TOOL_LIST, TASK, PROMPT_TEMPLATE, SOLVE_PROMPT, MODEL, PROMPT_TEMPLATE_2, TYPE_LIST
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Tongyi
from langgraph.graph import StateGraph, END
from config_api_keys import TAVILY_API_KEY, OPENAI_API_KEY, DASHSCOPE_API_KEY
from call_tools import use_actual_tool
from logger import *
from cache import *
from utils import *

# 设置环境变量
os.environ["LANGCHAIN_PROJECT"] = "ReWOO"
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY

class ReWOO(TypedDict):
    task: str
    plan_string: str
    steps: List
    results: dict
    result: str

# 初始化模型
# TODO：后续要替换为自己的本地Qwen模型
if MODEL == "qwen":
    model = Tongyi()
else:
    model = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo")

# 正则表达式
# 这是原本的表达式，但是容易识别不出steps
regex_pattern = r"Plan:\s*(.+)\s*(#E\d+)\s*=\s*(\w+)\s*\[([^\]]+)\]"

# 这个是新的表达式，能够对应API输入为空的情况，也不容易出现漏steps这种情况
regex_pattern = r"Plan:\s*(.+)\s*(#E\d+)\s*=\s*(\w+)\s*(?:\[(.*?)\])?"

prompt_template = ChatPromptTemplate.from_messages([("user", PROMPT_TEMPLATE)])

prompt_template_2 = ChatPromptTemplate.from_messages([("user", PROMPT_TEMPLATE_2)])

# planner其实就是一个agent，是模型+prompt
planner = prompt_template | model

planner_type = prompt_template_2 | model

def get_type(task:str):
    result = planner_type.invoke({"task": task, "type_list": ",".join(TYPE_LIST)})

    if MODEL != "qwen":
        result = result.content
    
    for type in TYPE_LIST:
        if type in result:
            return type
    return "general"

def get_types(task:str):

    result = planner_type.invoke({"task": task, "type_list": ",".join(TYPE_LIST)})

    logger.info(f"获取到的类型是：{result}")

    # result = result.split(',')
    type_list = []

    for type in TYPE_LIST:
        if type in result:
            type_list.append(type)
        
    logger.debug(f"获取到的类型是：{type_list}")
    return type_list
    
def get_plan(state: ReWOO):
    """生成任务计划。"""
    task = state["task"]

    # 改为qwen的话，会在这个部分出问题
    result = planner.invoke({"task": task, "tool_list": TOOL_LIST})

    # 如果是用OpenAI，这里的result都得改为result.content（一共有4个地方）
    # 如果是用Qwen，这里就保持result就好
    if MODEL == "qwen":
        logger.error(f"Qwen模型的回复：{result}")
    else:
        result = result.content
        logger.error(f"Qwen模型的回复：{result}")

    matches = re.findall(regex_pattern, result)
    logger.critical("计划步骤:")
    
    logger.debug(f"steps:{matches}")

    return {"steps": matches, "plan_string": result}

def _get_current_task(state: ReWOO):
    """确定当前任务步骤。"""
    if state["results"] is None:
        return 1
    if len(state["results"]) == len(state["steps"]):
        return None
    else:
        return len(state["results"]) + 1

def tool_execution(state: ReWOO):
    """执行计划中的工具。"""

    _step = _get_current_task(state)
    _, step_name, tool, tool_input = state["steps"][_step - 1]
    _results = state["results"] or {}

    for k, v in _results.items():
        tool_input = tool_input.replace(k, v)
    
    logger.info(f"Executing step {_step}: {step_name} using {tool} with input {tool_input}")
    
    # 专门来选择并执行工具
    result = use_actual_tool(tool, tool_input)

    logger.critical(f"工具执行结果呀：{result}")
    # result = "genv是2024年上映的一部美国超级英雄电视剧"

    _results[step_name] = str(result)
    return {"results": _results}

def solve(state: ReWOO):
    """根据收集的证据生成最终解决方案。"""
    plan = ""
    for _plan, step_name, tool, tool_input in state["steps"]:
        _results = state["results"] or {}
        for k, v in _results.items():
            tool_input = tool_input.replace(k, v)
            step_name = step_name.replace(k, v)
        plan += f"Plan: {_plan}\n{step_name} = {tool}[{tool_input}]\n"
    prompt = SOLVE_PROMPT.format(plan=plan, task=state["task"])
    result = model.invoke(prompt)
    if MODEL != "qwen":
        result = result.content

    return {"result": result}

def _route(state):
    """确定任务执行的下一步。"""
    _step = _get_current_task(state)
    if _step is None:
        # 如果所有的工具调用步骤都执行完了，就去执行solve，得到最终结果
        return "solve"
    else:
        # 如果工具调用步骤还没执行完，继续执行
        return "tool"

def rewoo_as_func(task: str):
    # cache有关的内容
    if search(task) is not None:
        return search(task)

    rewoo_state = ReWOO(task=task)
    # plan = get_plan(ReWOO(task="帮我查询北京的天气"))
    plan = get_plan(ReWOO(task=task))
    rewoo_state["plan_string"] = plan["plan_string"]
    rewoo_state["steps"] = plan["steps"]

    types= get_types(task)
    api_recommendations = get_tools_by_types(types)

    response = "\n\n**API编排步骤：**\n"
    
    for idx, step in enumerate(plan["steps"], 1):
        response += f"* 第{idx}步: \n思路：{step[0]}\t调用工具[{step[2]}]"
        if len(step[3]):
            response += f",工具的输入参数为:{step[3]}。\n\n"
        else:
            response += "。\n\n"

    # 同时要记得把这个plan存储起来，后续要用
    logger.debug("##############")
    logger.debug({"response": response, "plan_json": plan["steps"], "rewoo_state": rewoo_state})
    logger.debug("##############")

    api_response = {"response": response, "rewoo_state": rewoo_state, "api_recommendations": api_recommendations}

    add_to_cache(task, api_response)

    return api_response

def get_ready_plan(state: ReWOO):
    if "steps" in state and "plan_string" in state:
        return {"steps": state["steps"], "plan_string": state["plan_string"]}

    return get_plan(state)

def execute_plan(state: ReWOO = ReWOO(task="帮我查询北京的天气")):
    graph = StateGraph(ReWOO)

    # 理论上来讲，不需要重新执行获取计划的步骤了吧
    # get_plan可以替换为一个新的函数，这个函数直接使用规划好的计划
    graph.add_node("plan", get_ready_plan)
    # 直接使用规划好的计划，执行各种tools
    graph.add_node("tool", tool_execution)
    # 最后执行solve，得到最终结果
    graph.add_node("solve", solve)
    graph.add_edge("plan", "tool")
    graph.add_edge("tool", "solve")
    graph.add_edge("solve", END)
    graph.add_conditional_edges("tool", _route)
    graph.set_entry_point("plan")
    app = graph.compile()

    i = 1
    for s in app.stream(state):
        logger.debug(f"Step {i}: {s}")
    
    response = f"**API调用结果:**\n\n{s['solve']['result']}"

    return {"response": response}

if __name__ == "__main__":
    # 定义任务执行的状态图
    task = "我想搜一下最近的电影"
    response = rewoo_as_func("我想知道长沙的天气，还想查一下长沙的一些酒店??")
    print(response)
    # print("选择的类别是", get_type(task))