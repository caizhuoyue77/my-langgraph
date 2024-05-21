from typing import Union
from fastapi import FastAPI, Request
from memory_main import get_character_response, record_memory
from logger import *

app = FastAPI()

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
        # return {"response": "111", "memory": memory}
        return response

    return {"response": "No query provided", "memory": None}

@app.post("/record_memory")
async def record_memory_endpoint(request: Request):
    data = await request.json()
    messages = data.get("messages")

    return {"response": await record_memory(messages)}
