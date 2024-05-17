import json
import asyncio
from pydantic import BaseModel, Field
import aiohttp

async def search_flights_iter(from_id: str, to_id: str, depart_date: str, page_no: int, adults: int, children: str, currency_code: str):
    return "有1班飞机从上海飞往新加坡，航班号为1012466，票价为200元"
    
    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    querystring = {
        "fromId": from_id,
        "toId": to_id,
        "departDate": depart_date,
        "pageNo": str(page_no),
        "adults": str(adults),
        "children": children,
        "currency_code": currency_code
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=querystring) as response:
            if response.status == 200:
                return await response.json()  # Return the parsed JSON data
            else:
                return {"error": f"Failed to fetch flight data, status code: {response.status}"}

def search_flights(quert: str):
    from_id = "BOM.AIRPORT"
    to_id = "DEL.AIRPORT"
    depart_date = "2024-10-01"  # Replace <REQUIRED> with actual date
    page_no = 1
    adults = 1
    children = "0,17"
    currency_code = "CNY"
    return asyncio.run(get_flights_iter(from_id, to_id, depart_date, page_no, adults, children, currency_code))

class FlightSearchInput(BaseModel):
    from_id: str = Field(description="Airport code for the departure location")
    to_id: str = Field(description="Airport code for the destination location")
    depart_date: str = Field(description="Departure date")
    page_no: int = Field(default=1, description="Page number for pagination")
    adults: int = Field(default=1, description="Number of adults")
    children: str = Field(default="0", description="Comma-separated ages of children")
    currency_code: str = Field(description="Currency code")

if __name__ == "__main__":
    from_id = "BOM.AIRPORT"
    to_id = "DEL.AIRPORT"
    depart_date = "2024-10-01"  # Replace <REQUIRED> with actual date
    page_no = 1
    adults = 1
    children = "0,17"
    currency_code = "CNY"
    result = search_flights(from_id, to_id, depart_date, page_no, adults, children, currency_code)
    print("Answer:", result)
