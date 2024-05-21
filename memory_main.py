import os
import re
from typing import TypedDict, List
from config import PROMPT_TEMPLATE, MODEL, EXTRACT_MEMORY_PROMPT_TEMPLATE
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Tongyi
from langgraph.graph import StateGraph, END
from config_api_keys import OPENAI_API_KEY, DASHSCOPE_API_KEY
from logger import *
# from bge import bge_best_keys
# from bge_reranker import bge_reranker_best_keys
from bge_lsl import bge_best_keys
import json

# 设置环境变量
os.environ["LANGCHAIN_PROJECT"] = "ReWOO"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY


# 初始化模型
# TODO：后续要替换为自己的本地Qwen模型
if MODEL == "qwen":
    model = Tongyi()
else:
    model = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo")

prompt_template = ChatPromptTemplate.from_messages([("user", PROMPT_TEMPLATE)])
extract_memory_prompt_template = ChatPromptTemplate.from_messages([("user", EXTRACT_MEMORY_PROMPT_TEMPLATE)])

# character其实就是一个agent，是模型+prompt
character = prompt_template | model
memory_extractor = extract_memory_prompt_template | model

def get_memory(user_id: str):
    # 从数据库中获取用户的memory
    memory =  {
        "喜欢的食物":"麻婆豆腐",
        "喜欢的电影":"流浪地球",
        "喜欢的音乐":"周杰伦、林俊杰、薛之谦",
        "喜欢的书籍":"《三体》、《小妇人》、《白夜行》",
        "本科":"上海交通大学",
        "研究内容":"如何治好抑郁症",
        "最近在忙":"发毕业论文和在商汤科技实习",
        "爱好":"看电影、听音乐、看书、健身",
        "喜欢的动物":"猫咪，特别是布偶猫",
        "喜欢的颜色":"蓝色",
    }

    json_memory_file_name = '/nvme/chenweishu/code/memory_api/memory.json'

    try:
        with open(json_memory_file_name, 'r') as file:
            memory = json.load(file)
    except FileNotFoundError:
        logger.error("Memory data not found")

    return memory

async def get_relavant_memory(query:str, user_id: str):
    # 从数据库中获取用户的memory
    return filter_memory(query, get_memory(user_id))

def filter_memory(query:str, memory: dict, 
                  threshold: float = 0.45, top_k: int = 3, 
                  mode: str = "bge_reranker"):
    filered_memory = {}

    # 通过RAG，只获取直接有关的
    return memory

    if mode == "bge":
        return bge_best_keys(query, memory, threshold)
    else:
        return bge_reranker_best_keys(query, memory, top_k)

async def extract_memory(messages: str):
    # 从用户输入中提取信息
    return memory_extractor.invoke({"messages": messages})

async def record_memory(messages: str):
    memory = await extract_memory(messages)
    # 存储memory
    return memory

async def get_character_response(input: str):
    """生成任务计划。"""

    # url = "http://localhost:8000/retrieve-memory/"
    # import requests
    # # 从API获取用户的memory
    # response = requests.get(url)
    # if response.status_code == 200:
    #     memory = response.json()
    # else:
    #     memory = {}
    memory = get_memory("1")

    # 改为qwen的话，会在这个部分出问题
    msg = character.invoke({"input": input, "memory": memory})

    # 如果是用OpenAI，这里的result都得改为result.content（一共有4个地方）
    # 如果是用Qwen，这里就保持result就好
    if MODEL == "qwen":
        logger.error(f"Qwen模型的回复：{msg}")
    else:
        result = msg.content
        logger.error(f"OpenAI模型的回复：{result}")

    return {"response": msg, "memory": memory}
