import requests
from api_key_config import *
from bookings_search_hotel_destination import search_hotel_destination

def process_hotel_data(hotel_data):
    print("酒店的数据")
    print(hotel_data)

    hotels = []
    for hotel in hotel_data['data']['hotels']:
        item = {
            "name": hotel["property"]["name"],
            "reviewScore": hotel['property']['reviewScore'],
            "price": hotel["property"]["priceBreakdown"]
        }
        hotels.append(item)
    return {"hotels": hotels}

def validate_date(date: str):
    if len(date) != 10:
        return False
    if date[4] != '-' or date[7] != '-':
        return False
    return True
    

def search_hotels(destination: str):
    # Get the destination ID
    # dest_data = search_hotel_destination(destination)
    
    # if 'dest_id' in dest_data:
    #     dest_id = dest_data['dest_id']
    # else:
    #     return {"error": "Destination not found"}

    dest_id, arrival_date, departure_date = destination.split(',')[0], destination.split(',')[1].strip(), destination.split(',')[2].strip()

    print(f"dest_id: {dest_id}, arrival_date: {arrival_date}, departure_date: {departure_date}")

    if not validate_date(arrival_date) or not validate_date(departure_date):
        return {"error": "Invalid date format"}

    # Set default parameters
    params = {
        "dest_id": dest_id,
        "search_type": "CITY",
        "arrival_date": "2024-06-20",
        "departure_date": "2024-06-25",
        "adults": 1,
        "children_age": "",  # Provide an empty string if no children are present
        "room_qty": 1,
        "page_number": 1,
        "languagecode": "zh-cn",
        "currency_code": "CNY"
    }

    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
    headers = {
        "X-RapidAPI-Key": api_keys[0],
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return process_hotel_data(data)
        else:
            return {"error": f"Failed to search hotels, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

if __name__ == "__main__":
    result = search_hotels("shanghai")
    print("Answer:", result)