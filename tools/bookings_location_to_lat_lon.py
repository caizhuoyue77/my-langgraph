import json
import asyncio
from pydantic import BaseModel, Field
from api_key_config import *
import aiohttp

async def location_to_lat_lon_iter(query: str):
    url = "https://booking-com15.p.rapidapi.com/api/v1/meta/locationToLatLong"
    headers = {
        "X-RapidAPI-Key": api_keys[0],
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    params = {"query": query}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()  # Return the parsed JSON data
            else:
                return {"error": f"Failed to convert location to latitude and longitude, status code: {response.status}"}

def location_to_lat_lon(query: str):
    query="shanghai"
    return asyncio.run(location_to_lat_lon_iter(query))

class LocationToLatLonInput(BaseModel):
    query: str = Field(description="Location query to be converted to latitude and longitude coordinates")

if __name__ == "__main__":
    query = "man"
    result = location_to_lat_lon(query)
    print("Answer:", result)
