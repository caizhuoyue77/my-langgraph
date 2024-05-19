from typing import Union
from fastapi import FastAPI, Request
from rewoo import rewoo_as_func, execute_plan
from logger import *

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# TODO: 要改为get_plan之类的
@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    query = data.get("message")
    if query:
        response = rewoo_as_func(query)
        return response
    return {"response": "No query provided", "plan_json": None}

@app.post("/continue")
async def execute_endpoint(request: Request):
    data = await request.json()
    plan = data.get("plan")
    # 把在之前获取的plan传递给执行计划的函数
    if plan:
        response = execute_plan(plan)
        return response
    return {"response": "No plan provided"}
