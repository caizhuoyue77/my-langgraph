import json
import asyncio
from pydantic import BaseModel, Field
import requests

async def search_location_iter(location: str):
    base_url = "https://geoapi.qweather.com/v2/city/lookup"

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

def search_location(location: str):
    return asyncio.run(search_location_iter(location))

class LocationInput(BaseModel):
    location: str = Field(description="地点的名称，类似changsha")


if __name__ == "__main__":
    print(search_location("jiaxing"))
