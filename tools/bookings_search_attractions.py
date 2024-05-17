import json
import asyncio
from pydantic import BaseModel, Field
import aiohttp

async def search_attractions_iter(id: str, page: int, currency_code: str, language_code: str):
    url = "https://booking-com15.p.rapidapi.com/api/v1/attraction/searchAttractions"
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    params = {
        "id": id,
        "page": str(page),
        "currency_code": currency_code,
        "languagecode": language_code
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()  # Return the parsed JSON data
            else:
                return {"error": f"Failed to fetch attractions, status code: {response.status}"}

def search_attractions(query: str):
    id = "eyJwaW5uZWRQcm9kdWN0IjoiUFJ2cFpHVWxKWkN6IiwidWZpIjotMTkyNDQ2NX0="
    page = 1
    currency_code = "CNY"
    language_code = "zh-cn"
    return asyncio.run(search_attractions_iter(id, page, currency_code, language_code))

class AttractionSearchInput(BaseModel):
    id: str = Field(description="Unique identifier for the attraction")
    page: int = Field(default=1, description="Page number for pagination")
    currency_code: str = Field(description="Currency code for pricing information")
    language_code: str = Field(description="Language code for the response")

if __name__ == "__main__":
    id = "eyJwaW5uZWRQcm9kdWN0IjoiUFJ2cFpHVWxKWkN6IiwidWZpIjotMTkyNDQ2NX0="
    page = 1
    currency_code = "CNY"
    language_code = "zh-cn"
    result = search_attractions(id, page, currency_code, language_code)
    print("Answer:", result)
