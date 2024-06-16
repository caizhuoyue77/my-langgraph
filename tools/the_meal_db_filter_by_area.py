import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class FilterByAreaInput(BaseModel):
    area: str = Field(description="用于在TheMealDB数据库中过滤的地区。")

def process_filter_results(filter_results):
    return filter_results  # Customize this function based on the expected structure of the filter results.

async def filter_by_area_iter(area: str) -> dict:
    """
    Asynchronously filters TheMealDB using a specified area via the RapidAPI service.
    
    Args:
        area (str): The area to filter by.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://themealdb.p.rapidapi.com/filter.php"
    querystring = {"a": area}
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "themealdb.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_filter_results(response.json())
        else:
            return {"error": f"Failed to filter by area, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def filter_by_area(area: str) -> dict:
    """
    A synchronous wrapper function to filter TheMealDB by area.

    Args:
        area (str): The area to filter by.

    Returns:
        dict: The result from the asynchronous filter function, containing either the filter results or an error message.
    """
    return asyncio.run(filter_by_area_iter(area))

if __name__ == "__main__":
    filter_area = "Chinese"
    
    area_filter_results = filter_by_area(filter_area)
    print("Filter Results:", area_filter_results)