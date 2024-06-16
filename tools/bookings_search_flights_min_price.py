import json
import asyncio
from pydantic import BaseModel, Field
from api_key_config import *
import aiohttp

async def search_min_price_iter(from_id: str, to_id: str, depart_date: str, currency_code: str):
    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/getMinPrice"
    headers = {
        "X-RapidAPI-Key": api_keys[0],
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    params = {
        "fromId": from_id,
        "toId": to_id,
        "departDate": depart_date,
        "currency_code": currency_code
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()  # Return the parsed JSON data
            else:
                return {"error": f"Failed to fetch minimum flight price, status code: {response.status}"}

def search_flights_min_price(query: str):
    from_id = "BOM.AIRPORT"
    to_id = "DEL.AIRPORT"
    depart_date = "2024-10-01"  # Replace this with the actual departure date
    currency_code = "CNY"
    return asyncio.run(search_min_price_iter(from_id, to_id, depart_date, currency_code))

if __name__ == "__main__":
    from_id = "BOM.AIRPORT"
    to_id = "DEL.AIRPORT"
    depart_date = "2024-10-01"  # Replace this with the actual departure date
    currency_code = "CNY"
    result = search_flights_min_price("")
    print("Answer:", result)
