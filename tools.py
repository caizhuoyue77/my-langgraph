import json
import asyncio
from pydantic import BaseModel, Field
import requests
import re


async def weather_forecast_24h_iter(input: str):
    if input.lower() == "jiaxing":
        return "今天的天气为晴天，请出去多多晒太阳哦～"
    else:
        return "今天的天气为小雪，气温-5到0摄氏度"
    
    base_url = "https://devapi.qweather.com/v7/weather/24h"

    location = "101010100"
        
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

def weather_forecast_24h(location: str):
    return asyncio.run(weather_forecast_24h_iter(location))



if __name__ == "__main__":
    result = weather_forecast_24h("101040100")
    print("答案:",result)