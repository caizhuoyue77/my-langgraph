import json
import asyncio
from pydantic import BaseModel, Field
import requests

class BikePathInput(BaseModel):
    origin: str = Field(description="出发点，经纬度格式，如 '117.500244,40.417801'")
    destination: str = Field(description="目的地，经纬度格式，如 '117.500244,40.417801'")
    key: str = Field(description="用户在高德地图官网申请的 Web服务API 类型KEY")

async def gaode_bike_path_iter(input: BikePathInput):
    base_url = "https://restapi.amap.com/v4/direction/bicycling"
    params = {
        "origin": input.origin,
        "destination": input.destination,
        "key": input.key
    }

    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch biking path information, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def gaode_bike_path(input: BikePathInput):
    return asyncio.run(gaode_bike_path_iter(input))

if __name__ == "__main__":
    input_data = BikePathInput(
        origin="116.434307,39.90909",
        destination="116.434307,40.90909",
        key="8bf32c47badfa147e52467c46b442de9"
    )
    result = gaode_bike_path(input_data)
    print("答案:", json.dumps(result, ensure_ascii=False, indent=4))
