from typing import Union
from fastapi import FastAPI, Request, HTTPException
from rewoo import rewoo_as_func, execute_plan
from logger import *
import json
import os

app = FastAPI()

CACHE_FILE = "cache.json"

def read_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def write_cache(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/get_plan")
async def chat_endpoint(request: Request):
    data = await request.json()
    query = data.get("message")
    developer_mode = data.get("developer_mode")
    if query:
        response = rewoo_as_func(query, developer_mode)
        return response
    return {"response": "No query provided", "rewoo_state": None}


@app.post("/execute_plan")
async def execute_endpoint(request: Request):
    data = await request.json()
    state = data.get("rewoo_state")
    if state:
        logger.error(f"即将执行的计划: {state}")
        for step in state["steps"]:
            logger.error(step)
        response = execute_plan(state)
        return response
    return {"response": "No plan provided"}


@app.post("/delete")
async def delete_graph(request: Request):
    data = await request.json()
    graph_title = data.get("title")
    if not graph_title:
        raise HTTPException(status_code=400, detail="Title is required")

    cache_data = read_cache()
    if graph_title in cache_data:
        del cache_data[graph_title]
        write_cache(cache_data)
        return {"message": "Graph deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Graph not found")
