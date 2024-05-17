import json
import asyncio
from pydantic import BaseModel, Field
import aiohttp

async def search_flight_location_iter(query: str):
    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchDestination"
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    params = {"query": query}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()  # Return the parsed JSON data
            else:
                return {"error": f"Failed to fetch flight locations, status code: {response.status}"}

def search_flight_location(query: str):
    query = "shanghai"
    return asyncio.run(search_flight_location_iter(query))

class FlightLocationSearchInput(BaseModel):
    query: str = Field(default_factory=str, description="The search query string")

if __name__ == "__main__":
    query_string = "new"
    result = search_flight_location(query_string)
    print("Answer:", result)
