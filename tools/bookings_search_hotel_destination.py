import json
import asyncio
from pydantic import BaseModel, Field
import requests

async def search_hotel_destination_iter(destination: str):
    base_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"

    params = {"query":destination}

    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    try:
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch hotel destination information, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


def search_hotel_destination(destination: str):
    destination = "shanghai"
    return asyncio.run(search_hotel_destination_iter(destination))

class HotelDestinationInput(BaseModel):
    destination: str = Field(description="搜索酒店的地址")

if __name__ == "__main__":
    result = search_hotel_destination("shanghai")
    print("答案:",result)