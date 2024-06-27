import os
import re
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Tongyi
from langgraph.graph import StateGraph, END
from config import (
    TOOL_LIST,
    PROMPT_TEMPLATE,
    SOLVE_PROMPT,
    MODEL,
    FIND_TASK_TYPE_PROMPT_TEMPLATE,
    REWRITE_TASK_PROMPT_TEMPLATE,
    TYPE_LIST,
)
from config_api_keys import TAVILY_API_KEY, OPENAI_API_KEY, DASHSCOPE_API_KEY
from call_tools import use_actual_tool
from logger import logger
from cache import add_to_cache, search_cache
from utils import *

# 设置环境变量
os.environ["LANGCHAIN_PROJECT"] = "ReWOO"
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY


class ReWOO(TypedDict):
    """rewoo编排的基本单位"""

    task: str
    plan_string: str
    steps: List
    results: dict
    result: str
    api_recommendations: list
    api_kg: dict
    final_results: str


# 初始化模型
# TODO：后续要替换为自己的本地Qwen模型
if MODEL == "qwen":
    model = Tongyi()
else:
    model = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo")

REGEX_PATTERN = r"Plan:\s*(.+)\s*(#E\d+)\s*=\s*(\w+)\s*(?:\[(.*?)\])?"

prompt_template = ChatPromptTemplate.from_messages([("user", PROMPT_TEMPLATE)])
prompt_template_2 = ChatPromptTemplate.from_messages(
    [("user", FIND_TASK_TYPE_PROMPT_TEMPLATE)]
)
prompt_template_3 = ChatPromptTemplate.from_messages(
    [("user", REWRITE_TASK_PROMPT_TEMPLATE)]
)
# planner其实就是一个agent，是模型+prompt
planner = prompt_template | model
planner_type = prompt_template_2 | model
rewriter = prompt_template_3 | model


def get_types(task: str):
    """获取任务的类别"""
    result = planner_type.invoke({"task": task, "type_list": ",".join(TYPE_LIST)})
    logger.info(f"获取到的类型是：{result}")

    type_list = []
    for type in TYPE_LIST:
        if type in result:
            type_list.append(type)
    logger.debug(f"获取到的类型是：{type_list}")
    return type_list


def rewrite_task(task: str):
    """把任务重写为更加formal的格式"""
    return rewriter.invoke({"task": task})


def get_plan(state: ReWOO):
    """生成任务计划。"""
    task = state["task"]
    types = ["entertainment"]
    tools = get_tools_by_types(types)["tools"]
    result = planner.invoke(
        {"task": task, "tool_list": get_tool_list_str_from_json_list(tools)}
    )

    if MODEL == "qwen":
        logger.error(f"Qwen模型的回复：{result}")
    else:
        result = result.content
        logger.error(f"Qwen模型的回复：{result}")

    matches = re.findall(REGEX_PATTERN, result)
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

    logger.info(
        f"Executing step {_step}: {step_name} using {tool} with input {tool_input}"
    )

    result = use_actual_tool(tool, tool_input)
    logger.critical(f"工具执行结果呀：{result}")

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
        return "solve"
    else:
        return "tool"


def rewoo_as_func(task: str, developer_mode=True):
    """rewoo的编排内容"""
    from_cache = search_cache(task)
    if from_cache is not None:
        rewoo_state = search_cache(task)
        return {"response": "", "rewoo_state": rewoo_state, "api_recommendation": []}

    logger.debug("原任务:%s", task)
    task = rewrite_task(task)
    logger.debug("新任务:%s", task)

    rewoo_state = ReWOO(task=task)
    plan = get_plan(rewoo_state)
    rewoo_state["plan_string"] = plan["plan_string"]
    rewoo_state["steps"] = plan["steps"]

    types = get_types(task)
    nodes, edges = (
        get_tools_by_types(types)["tools"],
        get_tools_by_types(types)["edges"],
    )

    rewoo_state["api_recommendations"] = {"nodes": nodes, "edges": edges}

    print(get_related_nodes(nodes, get_sementic_nodes(), get_all_edges()))
    logger.error(nodes)

    rewoo_state["api_kg"] = {"nodes": nodes, "edges": get_all_edges()}
    response = "\n\n**API编排步骤：**\n"

    for idx, step in enumerate(plan["steps"], 1):
        response += f"* 第{idx}步: \n思路：{step[0]}\t调用工具[{step[2]}]"
        if len(step[3]):
            response += f",工具的输入参数为:{step[3]}。\n\n"
        else:
            response += "。\n\n"

    logger.debug("##############")
    logger.debug(
        {"response": response, "plan_json": plan["steps"], "rewoo_state": rewoo_state}
    )
    logger.debug("##############")

    if developer_mode == False:
        rewoo_state["final_results"] = execute_plan(rewoo_state)["response"]

    api_response = {"response": response, "rewoo_state": rewoo_state}
    return api_response


def get_ready_plan(state: ReWOO):
    """获取已有的计划"""
    if "steps" in state and "plan_string" in state:
        return {"steps": state["steps"], "plan_string": state["plan_string"]}


def execute_plan(state: ReWOO = ReWOO(task="帮我查询北京的天气")):
    """执行编排好的计划"""
    add_to_cache(state["task"], state)
    length = len(state["steps"])
    logger.info(f"计划的步骤数目是：{length}")

    list_of_steps = [list(t) for t in state["steps"]]
    j = 0
    change_dict = {}

    for step in list_of_steps:
        j += 1
        logger.info("看过来～看过来～")
        logger.info(step)
        if len(step[1]) != 0:
            change_dict[step[1]] = f"E{j}"
            old_step = step[1]
            new_step = f"#E{j}"
            step[1] = new_step
            step.append("changed")
            list_of_steps[j - 1] = step

            for step_ in list_of_steps:
                if "changed" not in step_ and len(step_[1]) > 0:
                    step_[-1] = step_[-1].replace(old_step, new_step)
        else:
            step.append("changed")
            step[1] = f"#E{j}"
            list_of_steps[j - 1] = step
            logger.info("这是新加入的步骤")

    logger.critical(list_of_steps)

    graph = StateGraph(ReWOO)
    graph.add_node("plan", get_ready_plan)
    graph.add_node("tool", tool_execution)
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
    get_plan(ReWOO(task="我想搜一下最近的电影"))
