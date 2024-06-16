import json
import asyncio
from pydantic import BaseModel, Field
from api_key_config import *
import aiohttp


async def get_exchange_rates_iter(base_currency:str):
    url = "https://booking-com15.p.rapidapi.com/api/v1/meta/getExchangeRates"
    headers = {
        "X-RapidAPI-Key": api_keys[0],
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    params = {"base_currency": base_currency}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()  # Return the parsed JSON data
            else:
                return {"error": f"Failed to fetch exchange rates, status code: {response.status}"}

def get_exchange_rates(base_currency: str):
    base_currency = "CNY"
    return asyncio.run(get_exchange_rates_iter(base_currency))

# if __name__ == "__main__":
#     base_currency = "CNY"
#     result = fetch_exchange_rates(base_currency)
#     print("Answer:", result)
