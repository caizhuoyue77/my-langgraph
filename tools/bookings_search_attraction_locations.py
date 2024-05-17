import json
import asyncio
from pydantic import BaseModel, Field
import aiohttp

async def search_attraction_locations(query: str, language_code: str):
    url = "https://booking-com15.p.rapidapi.com/api/v1/attraction/searchLocation"
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    params = {
        "query": query,
        "languagecode": language_code
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()  # Return the parsed JSON data
            else:
                return {"error": f"Failed to fetch attractions, status code: {response.status}"}

def search_attraction_locations(query: str):
    query = "shanghai"
    language_code = "zh-cn"
    return asyncio.run(search_attraction_locations(query, language_code))

class AttractionLocationSearchInput(BaseModel):
    query: str = Field(description="Search query for attractions")
    language_code: str = Field(description="Language code for the response")

if __name__ == "__main__":
    query = "shanghai"
    language_code = "zh-cn"
    result = search_attraction_locations(query, language_code)
    print("Answer:", result)
