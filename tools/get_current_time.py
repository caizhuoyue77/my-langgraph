import json
import asyncio
from pydantic import BaseModel, Field
import requests
import re
from datetime import datetime

async def get_current_time_iter(query:str):
    return datetime.now().strftime('现在的时间是：%Y年%m月%d日 %H点%M分%S秒')
   
def get_current_time(query:str):
    return asyncio.run(get_current_time_iter(query))

class TimeInput(BaseModel):
    query:str = Field(description="用户的query")