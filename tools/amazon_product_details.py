import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class AmazonProductDetailsInput(BaseModel):
    asin: str = Field(description="用于获取Amazon产品详情的ASIN码。")
    country: str = Field(default="US", description="用于搜索的国家代码。")

def process_product_details_results(product_details_results):
    important_fields = ['product_title', 'product_price', 'product_star_rating', 'product_url', 'product_description']
    parsed_data = {
        'status': product_details_results['status'],
        'request_id': product_details_results['request_id'],
        'data': {key: product_details_results['data'][key] for key in important_fields}
    }

    # Truncate the product description if it's too long
    if len(parsed_data['data']['product_description']) > 100:
        parsed_data['data']['product_description'] = parsed_data['data']['product_description'][:100] + '...'
    
    return parsed_data

async def amazon_product_details_iter(asin: str, country: str) -> dict:
    """
    Asynchronously retrieves Amazon product details using specified parameters via the RapidAPI service.
    
    Args:
        asin (str): The ASIN code for the product.
        country (str): The country code for the search.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://real-time-amazon-data.p.rapidapi.com/product-details"
    querystring = {
        "asin": asin,
        "country": country
    }
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "real-time-amazon-data.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_product_details_results(response.json())
        else:
            return {"error": f"Failed to retrieve Amazon product details, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def amazon_product_details(asin: str, country: str = "US") -> dict:
    """
    A synchronous wrapper function to retrieve Amazon product details.

    Args:
        asin (str): The ASIN code for the product.
        country (str): The country code for the search.

    Returns:
        dict: The result from the asynchronous product details function, containing either the product details results or an error message.
    """
    return asyncio.run(amazon_product_details_iter(asin, country))

if __name__ == "__main__":
    product_asin = "B07ZPKBL9V"  # Replace with your actual ASIN
    amazon_product_details_results = amazon_product_details(product_asin, country="US")
    print("Product Details Results:", amazon_product_details_results)
