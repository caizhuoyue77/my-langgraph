import json
import asyncio
from pydantic import BaseModel, Field
import requests
import re
# # from server.agent.tools.helper import get_location_id, get_date

async def sunrise_sunset_iter(input: str):
    base_url = "https://devapi.qweather.com/v7/astronomy/sun"

    # 写死了查询北京的信息
    location = "101010100"

    from datetime import datetime

    # 写死了查询当天的信息
    today = datetime.today()
    # 按照指定格式转换日期
    date = today.strftime("%Y%m%d")

    params = {
        "location": location,
        "date": date,
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

def sunrise_sunset(location: str):
    return asyncio.run(sunrise_sunset_iter(location))

class WeatherInput(BaseModel):
    location: str = Field(description="地点的ID，类似101010100的格式,如果不知道就要调用位置查询API")
    # date: str = Field(description="日期，yyyymmdd格式，比如20240425")

if __name__ == "__main__":
    result = sunrise_sunset("101040100")
    print("答案:",result)
