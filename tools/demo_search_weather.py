import json
import asyncio
from pydantic import BaseModel, Field
import requests
import re

async def search_weather_iter(location: str):

    print("search_weather_iter")

    return {"location":"101010100","weather":"晴转多云，可能会有小雨，记得带伞"}

    base_url = "http://162.105.88.82:57861/other/get_weather_info"

    text = "This is a sample text with 123 numbers in it."
    pattern = r"\d+"
    matches = re.findall(pattern, location)

    if(matches):
        print(matches)

    params = {
        "location": "101040100",
    }

    # 发送GET请求
    try:
        response = requests.get(base_url, params=params)

        # 检查响应状态码
        if response.status_code == 200:
            return response.json()  # 返回解析后的JSON数据
        else:
            return {"error": f"Failed to fetch weather information, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def search_weather(location: str):
    return asyncio.run(search_weather_iter(location))

class WeatherInput(BaseModel):
    location: str = Field(description="地点的ID")

if __name__ == "__main__":
    result = search_weather("101040100")
    print("答案:",result)
