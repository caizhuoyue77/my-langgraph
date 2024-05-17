import json
import asyncio
from pydantic import BaseModel, Field
import aiohttp

class HotelSearchInput(BaseModel):
    dest_id: str = Field(description="Destination ID for the hotel search")
    search_type: str = Field(description="Type of search, e.g., 'CITY'")
    arrival_date: str = Field(description="Arrival date at the hotel")
    departure_date: str = Field(description="Departure date from the hotel")
    adults: int = Field(description="Number of adults")
    children_age: str = Field(description="Comma-separated ages of children")
    room_qty: int = Field(description="Number of rooms required")
    page_number: int = Field(default=1, description="Page number for pagination")
    languagecode: str = Field(description="Language code for the response")
    currency_code: str = Field(description="Currency code for pricing")

async def search_hotels_iter(input: HotelSearchInput):
    return "上海的酒店有:1.希尔顿酒店 2000元 2.全季酒店 400元 3.汉庭酒店 200元"

    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    params = input.dict()  # Convert the Pydantic model to a dictionary for the query string
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()  # Return the parsed JSON data
            else:
                return {"error": f"Failed to search hotels, status code: {response.status}"}

def search_hotels(query: str):
    hotel_input = HotelSearchInput(
        dest_id="-2092174",
        search_type="CITY",
        arrival_date="2024-05-20",  # Replace <REQUIRED> with actual date
        departure_date="2024-05-25",  # Replace <REQUIRED> with actual date
        adults=1,
        children_age="0,17",
        room_qty=1,
        page_number=1,
        languagecode="zh-cn",
        currency_code="CNY"
    )
    return asyncio.run(search_hotels_iter(hotel_input))

if __name__ == "__main__":
    # Example use with hypothetical dates and other parameters
    hotel_input = HotelSearchInput(
        dest_id="-2092174",
        search_type="CITY",
        arrival_date="2024-05-20",  # Replace <REQUIRED> with actual date
        departure_date="2024-05-25",  # Replace <REQUIRED> with actual date
        adults=1,
        children_age="0,17",
        room_qty=1,
        page_number=1,
        languagecode="zh-cn",
        currency_code="CNY"
    )
    result = fetch_hotels(hotel_input)
    print("Answer:", result)
