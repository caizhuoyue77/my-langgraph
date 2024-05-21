from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import re
from utils import build_memory_prompt_cws, parse_to_json, update_json_data
from typing import Union
from fastapi import FastAPI, Request
from memory_main import get_character_response, record_memory
from logger import *

app = FastAPI()

# 设置GPU设备
os.environ['CUDA_VISIBLE_DEVICES'] = "3,4,5,6,7"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 模型和分词器的初始化
model_id = "/nvme/lisongling/models/Qwen1.5-14B-Chat"
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype="auto", device_map="auto", trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

# 从文件读取prompt_template
prompt_file_path = '/nvme/chenweishu/code/llama3chinese/longtermprompt1.txt'
with open(prompt_file_path, 'r', encoding='utf-8') as prompt_file:
    prompt_template = prompt_file.read()

json_memory_file_name = '/nvme/chenweishu/code/memory_api/memory.json'

# 存储记忆的 API
@app.post("/store-memory")
async def store_memory(request: Request):
    try:
        data = await request.json()
        user_name = data.get("user_name")
        bot_name = data.get("bot_name")
        messages = data.get("messages")
        prompt = build_memory_prompt_cws(user_name, bot_name, messages, prompt_template)
        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        model_inputs = tokenizer([text], return_tensors="pt").to(device)
        print(1)

        # 生成输出并解码
        generated_ids = model.generate(model_inputs.input_ids, max_new_tokens=1024)
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        print(2)
        
        answer = response.split('assistant')[2]
        print(answer)
        
        parse_to_json(answer, json_memory_file_name)
        # 返回所有的memory
        return {"response": "Memory stored successfully", "memory": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 取记忆的 API
@app.get("/retrieve-memory")
async def retrieve_memory():
    try:
        with open(json_memory_file_name, 'r') as file:
            memory_data = json.load(file)
        return JSONResponse(content=memory_data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Memory data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/chat_with_memory")
async def chat_endpoint(request: Request):
    data = await request.json()
    query = data.get("message")

    if query:
        response = await get_character_response(query)
        # memory = await record_memory(query)
        """
        response:对话模型的回复
        memory:一个json对象，对应有关的memory内容
        all_memory:一个json对象，对应目前该用户的所有memory内容
        """
        return response

    return {"response": "No query provided", "memory": None}

@app.post("/record_memory")
async def record_memory_endpoint(request: Request):
    data = await request.json()
    messages = data.get("messages")

    return {"response": await record_memory(messages)}