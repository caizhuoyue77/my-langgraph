import json
import asyncio
from pydantic import BaseModel, Field
import requests
import re
from qweather_search_location import *

async def weather_forecast_7d_iter(input: str):
    try:
        location = search_location("input")['location'][0]['id']
    except:
        location = '101010100'

    base_url = "https://devapi.qweather.com/v7/weather/7d"
    
    params = {
        "location": location,
        "key":"7fa7d0d9ef374dc78c32fd8f5cb444b7"
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

def weather_forecast_7d(location: str):
    return asyncio.run(weather_forecast_7d_iter(location))



if __name__ == "__main__":
    result = weather_forecast_7d("101040100")
    print("答案:",result)