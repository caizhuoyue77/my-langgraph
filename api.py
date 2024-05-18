from typing import Union
from fastapi import FastAPI, Request
from rewoo import rewoo_as_func

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    query = data.get("message")
    if query:
        # response = "在搞什么？"
        response = rewoo_as_func(query)
        return {"response": response}
    return {"response": "No query provided"}
