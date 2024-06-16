import json
import asyncio
from pydantic import BaseModel, Field
from api_key_config import *
import requests

async def get_languages_iter():

    return "中文是zh-cn 英文是us-en 没了"
    
    url = "https://booking-com15.p.rapidapi.com/api/v1/meta/getLanguages"
    headers = {
        "X-RapidAPI-Key":  api_keys[0],
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()  # 返回解析后的JSON数据
        else:
            return {"error": f"Failed to fetch languages, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def get_languages(query: str):
    return asyncio.run(get_languages_iter())

if __name__ == "__main__":
    result = get_languages("")
    print("答案:", result)