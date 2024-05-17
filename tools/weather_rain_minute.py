import json
import asyncio
from pydantic import BaseModel, Field
import requests
import re
from server.agent.tools.helper import get_location_id, get_lon_lat

async def weather_rain_minute_parse(response):
    return response["summary"]

async def weather_rain_minute_iter(input: str):
    base_url = "https://devapi.qweather.com/v7/minutely/5m"

    # 这个需要经纬度坐标，不能用location id了
    lonlat = get_lon_lat(input)
    
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
    result = weather_rain_minute("101040100")
    print("答案:",result)