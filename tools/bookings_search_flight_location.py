import asyncio
from pydantic import BaseModel, Field
from api_key_config import *
import aiohttp

async def extract_airport_ids(response):
    """
    从响应数据中提取所有type为AIRPORT的项的id。
    
    :param response: dict, 包含响应数据的字典
    :return: list, 包含所有type为AIRPORT的项的id
    """
    return [item['id'] for item in response['data'] if item['type'] == 'AIRPORT']

async def search_flight_location_iter(query: str):
    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchDestination"
    headers = {
        "X-RapidAPI-Key": api_keys[0],
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    params = {"query": query}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                json_response = await response.json()
                airport_ids = await extract_airport_ids(json_response)
                if len(airport_ids) == 0:
                    return {"error": "No airport found"}
                return airport_ids[0]
            else:
                return {"error": f"Failed to fetch flight locations, status code: {response.status}"}

def search_flight_location(query: str):
    return asyncio.run(search_flight_location_iter(query))

class FlightLocationSearchInput(BaseModel):
    query: str = Field(default_factory=str, description="The search query string")

if __name__ == "__main__":
    query_string = "hongkong"
    result = search_flight_location(query_string)
    print("Answer:", result)
