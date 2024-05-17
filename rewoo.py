import os
import re
import logging
from typing import TypedDict, List
from config import TOOL_LIST, TASK, PROMPT_TEMPLATE, SOLVE_PROMPT
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from config_api_keys import TAVILY_API_KEY, OPENAI_API_KEY
import colorlog

# 配置日志记录器
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'reset',
        'INFO': 'cyan',
        'WARNING': 'bold_yellow',
        'ERROR': 'bold_red',
        'CRITICAL': 'bold_red',
    },
    secondary_log_colors={},
    style='%'
))

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# 设置环境变量
os.environ["LANGCHAIN_PROJECT"] = "ReWOO"
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

class ReWOO(TypedDict):
    task: str
    plan_string: str
    steps: List
    results: dict
    result: str

# 初始化模型
# TODO：后续要替换为自己的本地模型
model = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo")

# 正则表达式
regex_pattern = r"Plan:\s*(.+)\s*(#E\d+)\s*=\s*(\w+)\s*\[([^\]]+)\]"

prompt_template = ChatPromptTemplate.from_messages([("user", PROMPT_TEMPLATE)])

# planner其实就是一个agent，是模型+prompt
planner = prompt_template | model

def get_plan(state: ReWOO):
    """生成任务计划。"""
    task = state["task"]
    result = planner.invoke({"task": task, "tool_list": TOOL_LIST})
    matches = re.findall(regex_pattern, result.content)
    logger.critical("计划步骤:")
    for step in matches:
        logger.critical(f"Plan: {step[0]}, {step[1]} = {step[2]}[{step[3]}]")
    return {"steps": matches, "plan_string": result.content}

def _get_current_task(state: ReWOO):
    """确定当前任务步骤。"""
    if state["results"] is None:
        return 1
    if len(state["results"]) == len(state["steps"]):
        return None
    else:
        return len(state["results"]) + 1

# TODO: 修改得更加智能一点，能够读取文件夹里的所有工具，然后
def use_actual_tool(tool: str, tool_input: dict):
    # 把对应的工具import进来
    from langchain_community.tools.tavily_search import TavilySearchResults
    from tools import weather_forcast_24h
    search = TavilySearchResults()
    weather_search = weather_forcast_24h


    if tool == "Google":
        result = search.invoke(tool_input)
    elif tool == "LLM":
        result = model.invoke(tool_input)
    elif tool == "WeatherSearch":
        result = weather_search(tool_input)
    elif tool == "HotelSearch":
        result = "长沙的酒店有：1.桔子水晶 2.如家 3.锦江之星"
    elif tool == "GetTime":
        result = "2024-05-20"
    else:
        raise ValueError(f"Unknown tool: {tool}")
    return result

def tool_execution(state: ReWOO):
    """执行计划中的工具。"""
    _step = _get_current_task(state)
    _, step_name, tool, tool_input = state["steps"][_step - 1]
    _results = state["results"] or {}

    for k, v in _results.items():
        tool_input = tool_input.replace(k, v)
    
    logger.info(f"Executing step {_step}: {step_name} using {tool} with input {tool_input}")
    
    # 写一个函数专门来选择并执行工具
    # execute_tool(tool, tool_input)

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
    return {"result": result.content}

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
    logger.info(f"Task:{task}")

    # 定义任务执行的状态图
    graph = StateGraph(ReWOO)
    graph.add_node("plan", get_plan)
    graph.add_node("tool", tool_execution)
    graph.add_node("solve", solve)
    # 添加边把他们串起来
    graph.add_edge("plan", "tool")
    graph.add_edge("solve", END)
    graph.add_conditional_edges("tool", _route)
    graph.set_entry_point("plan")
    app = graph.compile()

    i = 1

    response = ""
    for s in app.stream({"task": TASK}):
        logger.info(f"这是第{i}个流程")
        # response = response + str(s) + "\n"
        logger.info(s)
        if("plan" in s):
            j = 1
            response = "**API执行计划如下：**\n\n"
            for step in s['plan']['steps']:
                response = response + f"第{j}步：{step[0]}\n\n"
                j += 1
            logger.info(s['plan']['steps'])
        i += 1

    logger.info(s['solve']['result'])

    response = response + "\n\n**最终结果**：\n\n" + s['solve']['result'] + "\n"

    return response


if __name__ == "__main__":
    # 定义任务执行的状态图
    graph = StateGraph(ReWOO)
    graph.add_node("plan", get_plan)
    graph.add_node("tool", tool_execution)
    graph.add_node("solve", solve)
    # 添加边把他们串起来
    graph.add_edge("plan", "tool")
    graph.add_edge("solve", END)
    graph.add_conditional_edges("tool", _route)
    graph.set_entry_point("plan")
    app = graph.compile()

    i = 0
    for s in app.stream({"task": TASK}):
        i += 1
        logger.info(f"这是第{i}次循环")
        logger.info(s)

    logger.info(s['solve']['result'])