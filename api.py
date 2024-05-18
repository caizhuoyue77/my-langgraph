from typing import Union
from fastapi import FastAPI, Request
from rewoo import rewoo_as_func, execute_plan
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    query = data.get("message")
    if query:
        response,state = rewoo_as_func(query)
        state_str = json.dumps(state, ensure_ascii=False)
        return {"response": response, "state": state_str}
    return {"response": "No query provided"}

@app.post("/continue")
async def continue_endpoint(request: Request):
    data = await request.json()
    state_str = data.get("state")
    if state_str:
        state = json.loads(state_str)
        response = execute_plan(state)
        return {"response": response}
    return {"response": "No state provided"}