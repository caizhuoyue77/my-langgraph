import json
import asyncio
from pydantic import BaseModel, Field
import aiohttp

async def search_min_price_iter(from_id: str, to_id: str, depart_date: str, currency_code: str):
    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/getMinPrice"
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
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

def search_min_price(query: str):
    from_id = "BOM.AIRPORT"
    to_id = "DEL.AIRPORT"
    depart_date = "2024-10-01"  # Replace this with the actual departure date
    currency_code = "CNY"
    return asyncio.run(search_min_price_iter(from_id, to_id, depart_date, currency_code))

class MinPriceInput(BaseModel):
    from_id: str = Field(description="Airport code for the departure location")
    to_id: str = Field(description="Airport code for the destination location")
    depart_date: str = Field(description="Departure date")
    currency_code: str = Field(description="Currency code")

if __name__ == "__main__":
    from_id = "BOM.AIRPORT"
    to_id = "DEL.AIRPORT"
    depart_date = "2024-10-01"  # Replace this with the actual departure date
    currency_code = "CNY"
    result = fetch_min_price(from_id, to_id, depart_date, currency_code)
    print("Answer:", result)
