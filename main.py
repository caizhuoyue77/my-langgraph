from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import re

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

class DialogueInput(BaseModel):
    messages: str
    user_name: str = Field(default="用户")
    bot_name: str = Field(default="Default Bot")

# 存储记忆的 API
@app.post("/store-memory/")
async def store_memory(input_data: DialogueInput):
    try:
        prompt = build_memory_prompt_cws(input_data.user_name, input_data.bot_name, input_data.messages, prompt_template)
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
@app.get("/retrieve-memory/")
async def retrieve_memory():
    try:
        with open(json_memory_file_name, 'r') as file:
            memory_data = json.load(file)
        return JSONResponse(content=memory_data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Memory data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def update_json_data(existing_data, new_data):
    overwrite_keys = [
        "姓名", "年龄", "生日", "出生年份", "性别", "性取向", "民族/族群", "国籍", "星座", "生肖", "MBTI",
        "身高", "体重", "眼睛", "鼻子", "嘴唇", "脸型", "头发", "体型", "衣物", "饰品",
        "小学学校", "初中学校", "大学学校", "研究生学校", "博士学校", "现就读学校", "理想学校",
        "经济状况", "社会地位", "现住地", "出生地"
    ]
    
    for key, new_value in new_data.items():
        if new_value is None:
            continue  # Skip if new value is None
        if key in overwrite_keys:
            existing_data[key] = new_value  # Overwrite the value
        else:
            # Incremental update, ensure both old and new values are lists
            old_value = existing_data.get(key, [])
            if not isinstance(old_value, list):
                old_value = [old_value]
            if not isinstance(new_value, list):
                new_value = [new_value]
            # Merge and remove duplicates
            existing_data[key] = list(set(old_value + new_value))

    return existing_data

def parse_to_json(data, filename='data.json'):
    sections = data.strip().split("##")
    new_data = {}

    for section in sections:
        if section.strip():
            lines = section.strip().split("\n")
            for line in lines[1:]:
                line = line.lstrip('- ').strip()  # Remove "-" prefix and extra spaces
                key, value = None, None
                if ":" in line:
                    key, value = line.split(":", 1)
                elif "：" in line:
                    key, value = line.split("：", 1)

                if key and value:
                    key = key.strip()
                    value = value.strip()
                    if any(delimiter in value for delimiter in ';；,，'):
                        value = re.split('[;；,，]', value)
                        value = [v.strip() for v in value if v.strip()]
                    if value in ['空', '未知', '未提及']:
                        value = None
                    new_data[key] = value if value else None

    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
        updated_data = update_json_data(existing_data, new_data)
    else:
        updated_data = new_data

    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(updated_data, file, ensure_ascii=False, indent=4)

def build_memory_prompt_cws(user_name, bot_name, content, prompt):
    prompt = prompt.replace("<user_name>", user_name)
    prompt = prompt.replace("<bot_name>", bot_name)
    prompt = prompt.replace("{messages}", content)
    return prompt