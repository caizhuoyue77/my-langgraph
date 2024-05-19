from typing import Union
from fastapi import FastAPI, Request
from rewoo import rewoo_as_func, execute_plan
from logger import *

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# TODO: 要改为get_plan之类的
@app.post("/get_plan")
async def chat_endpoint(request: Request):
    data = await request.json()
    query = data.get("message")
    if query:
        response = rewoo_as_func(query)
        """
        包含response和plan_json两个字段
        response:自然语言的步骤
        rewoo_state:一个json对象，对应一个ReWOO的对象
        """
        return response
    return {"response": "No query provided", "rewoo_state": None}

@app.post("/execute_plan")
async def execute_endpoint(request: Request):
    data = await request.json()
    # data是request里面传递过来的内容
    state = data.get("rewoo_state")
    # 把在之前获取的plan传递给执行计划的函数
    if state:
        response = execute_plan(state)
        return response
    return {"response": "No plan provided"}