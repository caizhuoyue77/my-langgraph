import json
import asyncio
from pydantic import BaseModel, Field
from api_key_config import *
import aiohttp

async def get_currency_iter():
    url = "https://booking-com15.p.rapidapi.com/api/v1/meta/getCurrency"
    headers = {
        "X-RapidAPI-Key": api_keys[0],
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()  # Return the parsed JSON data
            else:
                return {"error": f"Failed to fetch currency data, status code: {response.status}"}

def get_currency(query:str):
    return asyncio.run(get_currency_iter())

if __name__ == "__main__":
    result = get_currency("")
    print("Answer:", result)
