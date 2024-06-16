import json
import asyncio
import requests

async def gaode_transit_path_iter(origin: str, destination: str, city: str, key: str):
    base_url = "https://restapi.amap.com/v3/direction/transit/integrated"
    params = {
        "origin": origin,
        "destination": destination,
        "city": city,
        "key": key,
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

def gaode_transit_path(origin: str, destination: str, city: str, key: str):
    return asyncio.run(gaode_transit_path_iter(origin, destination, city, key))

def extract_bus_lines(transits):
    bus_lines = []
    for transit in transits:
        for segment in transit['segments']:
            if 'bus' in segment:
                for bus_line in segment['bus']['buslines']:
                    bus_lines.append(bus_line['name'])
    return bus_lines

if __name__ == "__main__":
    origin = "116.481028,39.989643"
    destination = "116.434446,39.90816"
    city = "北京"
    key = "8bf32c47badfa147e52467c46b442de9"
    
    result = gaode_transit_path(origin, destination, city, key)
    
    if "route" in result and "transits" in result["route"]:
        transits = result["route"]["transits"]
        bus_lines = extract_bus_lines(transits)
        print("Bus Lines:")
        for line in bus_lines:
            print(line)
    else:
        print("结果中没有找到公交换乘信息。")
