import json
import asyncio
import requests

async def gaode_drive_path_iter(origin: str, destination: str, key: str, strategy: int = 0):
    base_url = "https://restapi.amap.com/v3/direction/driving"
    params = {
        "origin": origin,
        "destination": destination,
        "key": key,
        "strategy": strategy,
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

def gaode_drive_path(origin: str, destination: str, key: str, strategy: int = 0):
    return asyncio.run(gaode_drive_path_iter(origin, destination, key, strategy))

if __name__ == "__main__":
    origin = "116.481028,39.989643"
    destination = "116.465302,40.004717"
    key = "8bf32c47badfa147e52467c46b442de9"
    result = gaode_drive_path(origin, destination, key)
    print("答案:", json.dumps(result, ensure_ascii=False, indent=4))
