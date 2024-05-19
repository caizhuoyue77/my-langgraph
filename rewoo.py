import os
import re
from typing import TypedDict, List
from config import TOOL_LIST, TASK, PROMPT_TEMPLATE, SOLVE_PROMPT
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Tongyi
from langgraph.graph import StateGraph, END
from config_api_keys import TAVILY_API_KEY, OPENAI_API_KEY, DASHSCOPE_API_KEY
from call_tools import use_actual_tool
from qwen_model import QwenLLM
from logger import *

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
# 使用OpenAI模型
# model = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo")
# 使用Qwen的模型
model = Tongyi()
# TODO：后续要替换为自己的本地Qwen模型

# 正则表达式
# 这是原本的表达式，但是容易识别不出steps
regex_pattern = r"Plan:\s*(.+)\s*(#E\d+)\s*=\s*(\w+)\s*\[([^\]]+)\]"
# 新的表达式，可以比较好的识别出steps，但也许会有其他问题，先这样
regex_pattern = r"Plan:\s*(.*?)\s*#E\d+\s*=\s*([\w\[\]]+)"

prompt_template = ChatPromptTemplate.from_messages([("user", PROMPT_TEMPLATE)])

# planner其实就是一个agent，是模型+prompt
planner = prompt_template | model

def get_plan(state: ReWOO):
    """生成任务计划。"""
    task = state["task"]

    # 改为qwen的话，会在这个部分出问题
    result = planner.invoke({"task": task, "tool_list": TOOL_LIST})

    logger.error(f"Qwen模型的回复：{result}")

    # 如果是用OpenAI，这里的result都得改为result.content（一共有4个地方）
    # 如果是用Qwen，这里就保持result就好
    matches = re.findall(regex_pattern, result)
    logger.critical("计划步骤:")
    
    # for step in matches:
    #     logger.critical(f"Plan: {step[0]}, {step[1]} = {step[2]}[{step[3]}]")
    #     logger.critical(f"step:{step}")
    
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
    plan = get_plan(ReWOO(task="帮我查询北京的天气"))

    logger.debug(plan["steps"])

    response = "**API编排步骤：**\n"
    
    for idx, step in enumerate(plan["steps"], 1):
        response += f"* 第{idx}步: {step[0]}\n\n"

    # 同时要记得把这个plan存储起来，后续要用

    logger.debug("##############")
    logger.debug({"response": response, "plan_json": plan["steps"]})
    logger.debug("##############")

    return {"response": response, "plan_json": plan}

def get_ready_plan():
    plan = rewoo_as_func("现在几点？")["plan_json"]
    return plan

def execute_plan(state: ReWOO):

    graph = StateGraph(ReWOO)

    # 理论上来讲，不需要重新执行获取计划的步骤了吧
    # get_plan可以替换为一个新的函数，这个函数直接使用规划好的计划

    graph.add_node("plan", get_ready_plan)
    # 直接使用规划好的计划，执行各种tools
    graph.add_node("tool", tool_execution)
    # 最后执行solve，得到最终结果
    graph.add_node("solve", solve)
    graph.add_edge("plan", "tool")
    graph.add_edge("solve", END)

    graph.add_conditional_edges("tool", _route)
    graph.set_entry_point("tool")
    app = graph.compile()

    response = ""

    for s in app.stream(state):
        response += "1"
        # response += str(s)+'\n'
    
    response += "API调用结果:" + s['solve']['result']

    return response

        



if __name__ == "__main__":
    # 定义任务执行的状态图
    rewoo_as_func("我想知道长沙的天气，以及我等下要去长沙玩，能不能帮我查一下酒店?")