"""
Pass rate 和 win rate的定义
"""
from make_api_plan import get_chat_response

# prompt
PASS_RATE_PROMPT = "Tell me if this plan is applicable(pass/fails). The task:[task]. The plan:[plan]"

"""参考prompt
A.5 DETAILS FOR TOOLEVAL
We adopt two metrics for automatic tool-use capability evaluation: pass rate and win rate.
Details for Pass Rate To assess whether a solution path completes the tasks outlined in the original
instruction and successfully passes it, we need to first consider the solvability of the instruction. In
principle, an instruction can be classified as either (1) solvable: for example, at least one of the
provided tools is potentially helpful in solving the original instruction; or (2) unsolvable: for example,
all APIs are irrelevant to the instruction or the instruction provides invalid information such as invalid
email address.
To determine whether a solution path is deemed passed or not, we need to consider whether the
instruction is solvable or unsolvable. In our evaluation, three types of labels can be given to each
solution path, i.e., Pass, Fail, and Unsure. Specifically, we define different rules as follows:
If the instruction is solvable:
1. If the model gives finish type “Finish by Giving Up”,
(a) After trying all the APIs extensively during and receiving no helpful information from
APIs, the solution path is deemed a Pass.
(b) If the model only calls a few API or receiving valid information from the APIs, the
solution path is deemed a Fail.
2. If the model gives finish type “Finish with Final Answer”,
(a) If the APIs provide no valid information, and the model has tried all the APIs to retrieve
useful information, but the final answer still does not resolve the original instruction or
conveys a refusal (such as “I’m sorry, but I can’t provide you with this, because the
tools are unavailable”), the solution path is deemed a Pass.
(b) If the tools provide valid information, and the final answer does not completely resolve
the instruction or is a refusal, the solution path is deemed a Fail.
(c) If the final answer completely resolves the original instruction, the solution path is
deemed a Pass.
(d) If it is unable to determine if the instruction is resolved based on the content of the final
answer, the solution path is deemed an Unsure.
If the instruction is unsolvable:
1. If the model gives finish type “Finish with Final Answer”,
(a) If the final answer resolves an instruction that was initially considered unresolvable,
the solution path is deemed a Pass.
(b) If the final answer is a refusal, the solution path is deemed a Pass.
(c) If the final answer is hallucinated by the model itself and provides a false positive
response (such as “I’ve completed the task, the final answer is *”), the solution path is
deemed a Fail.
2. If the model gives finish type “Finish by Giving Up”,
(a) Under this case, the solution path is deemed a Pass.
For every solution path, we instruct the ChatGPT evaluator to generate multiple (≥4) predictions
and perform a majority vote to derive the final pass rate.
15
Preprint
Details for Win Rate Since pass rate only measures whether an instruction is completed or not,
instead of how well it is completed, we adopt another metric: win rate. It is measured by comparing
two solution paths for a given instruction. We assume that a passed candidate is better than a failed
candidate and only compare those solution paths that are both “Pass”, or both “Failed” annotated
by the ChatGPT evaluator. Note that compared with another solution path, one solution path will be
annotated with one of the following: win, lose, or tie. We build rules for the evaluator’s behavior
to decide which solution path is better, and the criteria are listed as follows:
1. Information richness: whether the final answer contains all the necessary information to
answer the original instruction. A significantly richer answer is better, while a similar level
of richness that is sufficient to answer the question ties.
2. Factuality: whether it accurately describes what has been done, and what failed in the end.
A more accurate description in the final answer is better.
3. Reasoning: whether a detailed and accurate reason for failure is provided if the query
remains unresolved. A more detailed reason is better.
4. Milestone: calculating the number of milestones reached during execution.
5. Exploration: whether more potentially useful APIs were attempted during the execution
process. The use of a greater number of APIs is better.
6. Cost: Having fewer repeated (redundant) API calls is better if the number of APIs used is
the same.
For every solution path, we also generate multiple (≥4) predictions and then perform a majority
vote to derive the final win rate. In Table 4, for ease of reading, we split the ratio of tie into two
pieces and add them to win and lose, respectively. In Table 6, we report the original numbers as a
reference.
"""


# 调用某个大模型来judge
def get_pass_score(query:str, plan_str:str):
    prompt = PASS_RATE_PROMPT.replace("[task]", query)
    prompt = prompt.replace("[plan]", plan_str)
    
    return get_chat_response(prompt)
