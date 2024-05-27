import json
import asyncio
from pydantic import BaseModel, Field
import aiohttp
from bookings_search_hotel_destination import *

async def process_hotel_data(hotel_data):
    hotels = []
    for hotel in hotel_data['data']['hotels']:
        item = {
            "name": hotel["property"]["name"],
            "reviewScore": hotel['property']['reviewScore'],
            "price": hotel["property"]["priceBreakdown"]
        }
        hotels.append(item)
    return {"hotels": hotels}

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
    query: str = Field(description="Search query for the hotel")

async def search_hotel_destination_iter(destination: str):
    base_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"
    params = {"query": destination}
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(base_url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to fetch hotel destination information, status code: {response.status}"}
        except aiohttp.ClientError as e:
            return {"error": f"Request failed: {str(e)}"}

async def search_hotels_iter(input: HotelSearchInput):
    dest_data = await search_hotel_destination_iter(input.query)
    if 'data' in dest_data and len(dest_data['data']) > 0:
        input.dest_id = dest_data['data'][0]['dest_id']
    else:
        return {"error": "Destination not found"}

    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    params = input.dict()

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return await process_hotel_data(data)
            else:
                return {"error": f"Failed to search hotels, status code: {response.status}"}

def search_hotels(query: str):
    hotel_input = HotelSearchInput(
        dest_id="-1924465",
        search_type="CITY",
        arrival_date="2024-06-20",
        departure_date="2024-06-25",
        adults=1,
        room_qty=1,
        page_number=1,
        languagecode="zh-cn",
        currency_code="CNY",
        query=query
    )
    loop = asyncio.get_event_loop()
    if loop.is_running():
        task = loop.create_task(search_hotels_iter(hotel_input))
        result = loop.run_until_complete(task)
    else:
        result = asyncio.run(search_hotels_iter(hotel_input))
    return result

if __name__ == "__main__":
    result = search_hotels("shanghai")
    print("Answer:", result)
