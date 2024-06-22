import os
from utils import get_tool_list_str

TOOL_LIST = get_tool_list_str()

MODEL = "qwen"  # qwen或者gpt-3.5

# 可以在这里指定
TASK = "我想知道长沙的天气，以及我等下要去长沙玩，能不能帮我查一下酒店?"

TYPE_LIST = [
    "general",
    "travel",
    "weather",
    "entertainment",
    "news",
    "food",
    "shopping",
]

REWRITE_TASK_PROMPT_TEMPLATE = """对于自然语言的任务:{task}，请你提取出其中需要完成的任务，比如把：明天长沙的天气如何？在帮我查查酒店呗。 提取为：1.搜索明天长沙的天气 2.搜索长沙的酒店 请直接输出任务，不需要解释。"""

FIND_TASK_TYPE_PROMPT_TEMPLATE = """对于任务{task},请你判断任务的类别，在以下几种中进行选择：
{type_list}\n请直接输出类别的名称，不需要输出任何其他内容。注意，如果你想选择多个类别，请用逗号分隔不同类别。"""

PROMPT_TEMPLATE = """For the following task, make plans that can solve the problem step by step. For each plan, indicate \
which external tool or API together with tool input to retrieve evidence. You can store the evidence into a \
variable #E that can be called by later tools. (Plan, #E1, Plan, #E2, Plan, ...)

Tools can be one of the following:
{tool_list}

For example,
Task: I will stay in shanghai from 2024-06-01 to 2024-06-03. I want to find some hotels.
Plan: Use the SearchHotelDestination tool to find the destination ID of shanghai.
#E1 = SearchHotelDestination[shanghai]

Plan: Use the dest_id from #E1 and the dates to call SearchHotels to find the available hotels.
#E2 = SearchHotels[#E1, 2024-06-01, 2024-06-03, 1]

Task: 你能告诉我上海最近1天的天气吗?
Plan: Use the SearchLocation tool to find the location ID of shanghai.
#E1 = SearchLocation[shanghai]

Plan: Use the location id from #E1 to call WeatherForecast24H to get the weather forecast.
#E2 = WeatherForecast24H[#E1]

Task: 帮我搜索一下上海飞长沙的机票，出发时间是2024年12月1日。
Plan: Use the SearchFlightLocation tool to find the airport ID of shanghai.
#E1 = SearchFlightLocation[shanghai]

Plan: Use the SearchFlightLocation tool to find the airport ID of changsha.
#E2 = SearchFlightLocation[changsha]

Plan: Use the airport ids from #E1 and #E2 and the date to call SearchFlights to find the available flights.
#E3 = SearchFlights[#E1, #E2, 2024-12-01]

Begin! 
Caution: 
1.You can only use the tools listed above. Do not use any other tools or APIs. 
2.Describe your plans with rich details.
3.Each Plan should be followed by only one #E.
4.Parameters should be in English.

Task: {task}
Response: """

SOLVE_PROMPT = """Solve the following task or problem. To solve the problem, we have made step-by-step Plan and \
retrieved corresponding Evidence to each Plan. Use them with caution since long evidence might \
contain irrelevant information. Use bullet points to list the key points of the evidence whenever possible. \

{plan}

Now solve the question or task according to provided Evidence above. 
Respond with the answer and detailed explaination.(But be consice and clear)

Task: {task}
Response:"""


if __name__ == "__main__":
    print(TOOL_LIST)
