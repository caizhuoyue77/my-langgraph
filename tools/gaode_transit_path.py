import json
import asyncio
from pydantic import BaseModel, Field
import requests

class TransitPathInput(BaseModel):
    origin: str = Field(description="出发点，经纬度格式，如 '117.500244,40.417801'")
    destination: str = Field(description="目的地，经纬度格式，如 '117.500244,40.417801'")
    city: str = Field(description="起点城市名称或 citycode")
    key: str = Field(description="用户在高德地图官网申请的 Web服务API 类型KEY")

async def gaode_transit_path_iter(input: TransitPathInput):
    base_url = "https://restapi.amap.com/v3/direction/transit/integrated"
    params = {
        "origin": input.origin,
        "destination": input.destination,
        "city": input.city,
        "key": input.key,
        "output": "JSON"
    }

    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch transit path information, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def gaode_transit_path(input: TransitPathInput):
    return asyncio.run(gaode_transit_path_iter(input))

if __name__ == "__main__":
    input_data = TransitPathInput(
        origin="116.481028,39.989643",
        destination="116.434446,39.90816",
        city="北京",
        key="8bf32c47badfa147e52467c46b442de9",
        strategy=0
    )
    result = gaode_transit_path(input_data)
    for key in result:
        print(key)
    
    route = result["route"]

    print(route)

    print("\n\nkeys in route")

    print("\n\nroute['origin']\n\n")

    print(route['origin'])

    print("\n\nroute['origin']\n\n")
    print(route['destination'])

    print("\n\nroute['distance']\n\n")
    print(route['distance'])

    print("\n\nroute['taxi_cost']\n\n")
    print(route['taxi_cost'])

    print("\n\nroute['transits']\n\n")
    print(route['transits'])

    # for key in route:
    #     print(key)

    

