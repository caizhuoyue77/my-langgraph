import json
import asyncio
from pydantic import BaseModel, Field
import aiohttp

def process_flight_data(response):
    flight_info = []
    # print(response)
    
    for offer in response['data']['flightOffers']:
        segments = []
        for segment in offer['segments']:
            for leg in segment['legs']:
                segment_info = {
                    "departure_airport": leg['departureAirport']['name'],
                    "departure_city": leg['departureAirport']['cityName'],
                    "departure_country": leg['departureAirport']['countryName'],
                    "arrival_airport": leg['arrivalAirport']['name'],
                    "arrival_city": leg['arrivalAirport']['cityName'],
                    "arrival_country": leg['arrivalAirport']['countryName'],
                    "departure_time": leg['departureTime'],
                    "arrival_time": leg['arrivalTime'],
                    "cabin_class": leg['cabinClass'],
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
    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }

    # 主要是fromId和toID，还有departDate三个参数需要填写

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
                return process_flight_data(response_data)  # Return the parsed JSON data
            else:
                return {"error": f"Failed to fetch flight data, status code: {response.status}"}

def search_flights(query: str):
    from_id = "SHA.AIRPORT"
    to_id = "HKG.AIRPORT"
    depart_date = "2024-07-01"  # Replace <REQUIRED> with actual date
    page_no = 1
    adults = 1
    children = "0,17"
    currency_code = "CNY"
    return asyncio.run(search_flights_iter(from_id, to_id, depart_date, page_no, adults, children, currency_code))

if __name__ == "__main__":
    result = search_flights("")
    print("Answer:", result)
