import json
import asyncio
from pydantic import BaseModel, Field
import requests
import re
from qweather_search_location import *


async def weather_rain_minute_parse(response):
    return response["summary"]

async def weather_rain_minute_iter(input: str):
    try:
        lon = search_location("input")['location'][0]['lon']
        lat = search_location("input")['location'][0]['lat']
        lonlat = lon + ',' + lat
    except:
        lonlat = "120.75086,30.76265"

    base_url = "https://devapi.qweather.com/v7/minutely/5m"
    
    params = {
        "location": lonlat,
        "key":"7fa7d0d9ef374dc78c32fd8f5cb444b7"
    }

    # 发送GET请求
    try:
        response = requests.get(base_url, params=params)

        # 检查响应状态码
        if response.status_code == 200:
            return await weather_rain_minute_parse(response.json())
        else:
            return {"error": f"Failed to fetch weather information, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def weather_rain_minute(input: str):
    return asyncio.run(weather_rain_minute_iter(input))

class RainInput(BaseModel):
    location: str = Field(description="经纬度格式，经度在前，纬度在后。例如:116.41,39.92。")

if __name__ == "__main__":
    result = weather_rain_minute("jiaxing")
    print("答案:",result)