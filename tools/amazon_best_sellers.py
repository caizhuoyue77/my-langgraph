import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class AmazonBestSellersInput(BaseModel):
    type: str = Field(default="BEST_SELLERS", description="要查询的类别类型。")
    page: int = Field(default=1, description="搜索结果的页码。")
    country: str = Field(default="US", description="用于搜索的国家代码。")

def process_best_sellers_results(best_sellers_results):
    return best_sellers_results  # Customize this function based on the expected structure of the best sellers results.

async def amazon_best_sellers_iter(type: str, page: int, country: str) -> dict:
    """
    Asynchronously retrieves Amazon best sellers using specified parameters via the RapidAPI service.
    
    Args:
        type (str): The type of best sellers to retrieve.
        page (int): The page number of search results.
        country (str): The country code for the search.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://real-time-amazon-data.p.rapidapi.com/best-sellers"
    querystring = {
        "type": type,
        "page": page,
        "country": country
    }
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "real-time-amazon-data.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_best_sellers_results(response.json())
        else:
            return {"error": f"Failed to retrieve Amazon best sellers, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def amazon_best_sellers(type: str = "BEST_SELLERS", page: int = 1, country: str = "US") -> dict:
    """
    A synchronous wrapper function to retrieve Amazon best sellers.

    Args:
        type (str): The type of best sellers to retrieve.
        page (int): The page number of search results.
        country (str): The country code for the search.

    Returns:
        dict: The result from the asynchronous best sellers function, containing either the best sellers results or an error message.
    """
    return asyncio.run(amazon_best_sellers_iter(type, page, country))

if __name__ == "__main__":
    best_sellers_type = "BEST_SELLERS"  # Replace with your actual type if different
    amazon_best_sellers_results = amazon_best_sellers(type=best_sellers_type, page=1, country="US")
    print("Best Sellers Results:", amazon_best_sellers_results)
