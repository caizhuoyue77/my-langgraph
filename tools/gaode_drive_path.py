import json
import asyncio
from pydantic import BaseModel, Field
import requests

class DrivePathInput(BaseModel):
    origin: str = Field(description="出发点，经纬度格式，如 '117.500244,40.417801'")
    destination: str = Field(description="目的地，经纬度格式，如 '117.500244,40.417801'")
    key: str = Field(description="用户在高德地图官网申请的 Web服务API 类型KEY")
    strategy: int = Field(default=0, description="驾车选择策略，详见文档")

async def gaode_drive_path_iter(input: DrivePathInput):
    base_url = "https://restapi.amap.com/v3/direction/driving"
    params = {
        "origin": input.origin,
        "destination": input.destination,
        "key": input.key,
        "strategy": input.strategy,
        "output": "JSON"
    }

    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch driving path information, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def gaode_drive_path(input: DrivePathInput):
    return asyncio.run(gaode_drive_path_iter(input))

if __name__ == "__main__":
    input_data = DrivePathInput(
        origin="116.481028,39.989643",
        destination="116.465302,40.004717",
        key="your_api_key_here"
    )
    result = gaode_drive_path(input_data)
    print("答案:", json.dumps(result, ensure_ascii=False, indent=4))
