import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class FilterByCategoryInput(BaseModel):
    category: str = Field(description="用于在TheMealDB数据库中过滤的类别。")

def process_filter_results(filter_results):
    return filter_results  # Customize this function based on the expected structure of the filter results.

async def filter_by_category_iter(category: str) -> dict:
    """
    Asynchronously filters TheMealDB using a specified category via the RapidAPI service.
    
    Args:
        category (str): The category to filter by.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://themealdb.p.rapidapi.com/filter.php"
    querystring = {"c": category}
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "themealdb.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_filter_results(response.json())
        else:
            return {"error": f"Failed to filter by category, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def filter_by_category(category: str) -> dict:
    """
    A synchronous wrapper function to filter TheMealDB by category.

    Args:
        category (str): The category to filter by.

    Returns:
        dict: The result from the asynchronous filter function, containing either the filter results or an error message.
    """
    return asyncio.run(filter_by_category_iter(category))

if __name__ == "__main__":
    filter_category = "Pasta"  # Replace 'Seafood' with your actual category
    category_filter_results = filter_by_category(filter_category)
    print("Filter Results:", category_filter_results)
