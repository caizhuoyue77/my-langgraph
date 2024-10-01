SELECT_CATEGORY_PROMPT = """

For every input user query.
Select the categories of the external tool you need:
{category_list}

Instructions:
- You should only give the category name. 
- You should choose the most relevant category for the user query.
- If you think that the user query is not relevant to any of the categories, you can choose the "other" category.
- If you can answer this query without using any external tool, you can choose the "none" category.

Example:
{few_shot_example}
"""

REACT_PROMPT = """
Please help sovle this problem using the following APIs.

# Problem
[query]

# APIs you can use:
[api_list]

# Output format
Reason:
Action:
Observation:
"""

COT_PROMPT = """
Please help sovle this problem using the following APIs.

# Problem
[query]

# APIs you can use:
[api_list]

# Output format

Let's think step by step.
"""

REFLEXION_PROMPT_PLAN = """
"""

REFLEXION_PROMPT_REFLECT = """
Please reflect on this ... and try to analyze the promblem.

# Follow this format:
Problem:
Possible solution:

NOTE: If there's no problem, output: None in both fields.
"""

PASS_RATE_PROMPT = """
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

用户指令：{query}
工具列表：{tool_list}
解决路径：{path}
最终回答：{final_answer}

你的评判：
"""


WIN_RATE_PROMPT = """

你是一个严格的评判者，为了解决用户指令：{query}。下面是两个不同模型提供的解决路径和最终回答。
请你帮我对比两条路径，然后给我提供胜/负/平三种中的一种判断结果。

# 评判标准
1. 信息丰富性：最终答案是否包含了回答原始指令所需的所有信息。信息明显更丰富的答案更好，而信息量相当的答案将视为平局。
2. 真实性：是否准确描述了完成了什么，以及最终失败的原因。更准确的描述优胜。
3. 推理：如果查询未解决，是否提供了详细且准确的失败原因。原因描述更详细者优胜。
4. 里程碑：计算执行过程中达到的里程碑数量。
5. 探索性：执行过程中是否尝试了更多有潜力的API。使用更多API的解决路径更优。
6. 成本：如果使用的API数量相同，则重复调用API较少者更优。

# 例子
...

# 需要判断的案例

用户指令:{query}
工具列表:{tool_list}
路径1:{path1}
回答1:{final_answer1}
路径2:{path2}
回答2:{final_answer2}

请你判断路径1是胜/负还是平。只需要输出正，负，或者平。

"""