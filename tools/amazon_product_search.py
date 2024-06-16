import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class AmazonProductSearchInput(BaseModel):
    query: str = Field(description="用于在Amazon数据库中搜索的查询字符串。")
    page: int = Field(default=1, description="搜索结果的页码。")
    country: str = Field(default="US", description="用于搜索的国家代码。")
    sort_by: str = Field(default="RELEVANCE", description="搜索结果的排序方式。")
    product_condition: str = Field(default="ALL", description="产品的状态。")

def process_search_results(search_results):
    important_fields = ['product_title', 'product_price', 'product_url']
    parsed_data = {
        'status': search_results['status'],
        'request_id': search_results['request_id'],
        'data': {
            'total_products': search_results['data']['total_products'],
            'country': search_results['data']['country'],
            'domain': search_results['data']['domain'],
            'products': []
        }
    }

    for product in search_results['data']['products'][:5]:
        parsed_product = {key: product[key] for key in important_fields}
        parsed_data['data']['products'].append(parsed_product)
    
    return parsed_data

async def amazon_product_search_iter(query: str, page: int, country: str, sort_by: str, product_condition: str) -> dict:
    """
    Asynchronously searches Amazon using specified parameters via the RapidAPI service.
    
    Args:
        query (str): The search query string.
        page (int): The page number of search results.
        country (str): The country code for the search.
        sort_by (str): The sorting method for the search results.
        product_condition (str): The condition of the products.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://real-time-amazon-data.p.rapidapi.com/search"
    querystring = {
        "query": query,
        "page": page,
        "country": country,
        "sort_by": sort_by,
        "product_condition": product_condition
    }
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "real-time-amazon-data.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_search_results(response.json())
        else:
            return {"error": f"Failed to search Amazon, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def amazon_product_search(query: str, page: int = 1, country: str = "US", sort_by: str = "RELEVANCE", product_condition: str = "ALL") -> dict:
    """
    A synchronous wrapper function to search Amazon.

    Args:
        query (str): The search query string.
        page (int): The page number of search results.
        country (str): The country code for the search.
        sort_by (str): The sorting method for the search results.
        product_condition (str): The condition of the products.

    Returns:
        dict: The result from the asynchronous search function, containing either the search results or an error message.
    """
    return asyncio.run(amazon_product_search_iter(query, page, country, sort_by, product_condition))

if __name__ == "__main__":
    search_query = "kindle"  # Replace 'Phone' with your actual search query
    amazon_search_results = amazon_product_search(search_query, page=1, country="US", sort_by="RELEVANCE", product_condition="ALL")
    print("Search Results:", amazon_search_results)
