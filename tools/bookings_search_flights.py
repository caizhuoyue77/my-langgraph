import json
import asyncio
from pydantic import BaseModel, Field
from api_key_config import *
import aiohttp
import re

def process_flight_data(response):
    """
    处理航班数据，提取所需信息。
    """
    flight_info = []
    
    for offer in response['data']['flightOffers'][:10]:
        segments = []
        for segment in offer['segments']:
            for leg in segment['legs']:
                segment_info = {
                    "departure_airport": leg['departureAirport']['name'],
                    # "departure_city": leg['departureAirport']['cityName'],
                    "arrival_airport": leg['arrivalAirport']['name'],
                    # "arrival_city": leg['arrivalAirport']['cityName'],
                    "departure_time": leg['departureTime'],
                    "arrival_time": leg['arrivalTime'],
                    # "cabin_class": leg['cabinClass'],
                    "flight_number": leg['flightInfo']['flightNumber'],
                    "carrier": leg['carriersData'][0]['name']
                }
                segments.append(segment_info)

        price_info = {
            "currency": offer['priceBreakdown']['total']['currencyCode'],
            "total_price": offer['priceBreakdown']['total']['units'] + offer['priceBreakdown']['total']['nanos'] / 1e9
        }

        flight_detail = {
            "segments": segments,
            "price": price_info
        }
        
        flight_info.append(flight_detail)

    return {"flights": flight_info}

async def search_flights_iter(from_id: str, to_id: str, depart_date: str, page_no: int, adults: int, children: str, currency_code: str):
    """
    异步搜索航班信息。
    """
    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
    headers = {
        "X-RapidAPI-Key": api_keys[0],
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
                response_data = await response.json()
                return process_flight_data(response_data)
            else:
                return {"error": f"Failed to fetch flight data, status code: {response.status}"}

def validate_input(from_id: str, to_id: str, depart_date: str):
    """
    验证输入参数的格式。
    """
    if not from_id.endswith(".AIRPORT"):
        from_id = "SHA.AIRPORT"
    if not to_id.endswith(".AIRPORT"):
        to_id = "HKG.AIRPORT"
    
    if not re.match(r"\d{4}-\d{2}-\d{2}", depart_date):
        depart_date = "2024-11-01"
    
    return from_id, to_id, depart_date

def search_flights(query: str):
    """
    根据查询字符串搜索航班信息。
    """
    from_id, to_id, depart_date = [x.strip() for x in query.split(",")]
    from_id, to_id, depart_date = validate_input(from_id, to_id, depart_date)
    
    page_no = 1
    adults = 1
    children = ""
    currency_code = "CNY"
    
    return asyncio.run(search_flights_iter(from_id, to_id, depart_date, page_no, adults, children, currency_code))

if __name__ == "__main__":
    result = search_flights("BOM.AIRPORT, HKG.AIRPORT, 2024-07-01")
    print("Answer:", result)