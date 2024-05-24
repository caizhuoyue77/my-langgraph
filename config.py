import os
from utils import get_tool_list_str

TOOL_LIST = get_tool_list_str()

MODEL = "qwen" # qwen或者gpt-3.5

# 可以在这里指定
TASK = "我想知道长沙的天气，以及我等下要去长沙玩，能不能帮我查一下酒店?"

TYPE_LIST = ["general","travel","weather","entertainment"]

PROMPT_TEMPLATE_2 = """对于任务{task},请你判断任务的类别，在以下几种中进行选择：
{type_list}\n请直接输出类别的名称，不需要输出任何其他内容。注意，如果你想选择多个类别，请用逗号分隔不同类别。"""

PROMPT_TEMPLATE = """For the following task, make plans that can solve the problem step by step. For each plan, indicate \
which external tool or API together with tool input to retrieve evidence. You can store the evidence into a \
variable #E that can be called by later tools. (Plan, #E1, Plan, #E2, Plan, ...)

Tools can be one of the following:
{tool_list}

For example,
Task: I want to know the weather today in the capital of France.
Plan: Use the WeatherSearch tool to find the current weather in the capital of France, which is Paris.
#E1 = WeatherForecast24H[Paris]

Task: I want to know the weather today in changsha and find a hotel.
Plan: Use the WeatherSearch tool to find the current weather in changsha.
#E1 = WeatherForecast24H[changsha]

Plan: Use the GetTime tool to get the date.
#E2 = GetTime[]

Plan: Use the HotelSearch tool to find the available hotels in changsha on the date.
#E3 = HotelSearch[changsha, #E2]

Begin! 
Caution: You can only use the tools listed above. Do not use any other tools or APIs. 
Describe your plans with rich details. Each Plan should be followed by only one #E.

Task: {task}"""

SOLVE_PROMPT = """Solve the following task or problem. To solve the problem, we have made step-by-step Plan and \
retrieved corresponding Evidence to each Plan. Use them with caution since long evidence might \
contain irrelevant information.

{plan}

Now solve the question or task according to provided Evidence above. Respond with the answer
directly with no extra words.

Task: {task}
Response:(请用中文)"""


if __name__ == "__main__":
    print(TOOL_LIST)