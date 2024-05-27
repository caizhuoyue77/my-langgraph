import json
import requests
from pydantic import BaseModel, Field

def search_hotel_destination(destination: str):
    base_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"
    
    params = {"query": destination}
    
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    
    try:
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code == 200:
            # 只返回第一个结果的dest_id
            return response.json()["data"][0]["dest_id"]
        else:
            return {"error": f"Failed to fetch hotel destination information, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

if __name__ == "__main__":
    result = search_hotel_destination("shanghai")
    print("答案:", result)
