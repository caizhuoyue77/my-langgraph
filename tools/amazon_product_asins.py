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

def extract_asin_from_url(url):
    return url.split("/")[-1]

def process_search_results(search_results):
    asins = []

    for product in search_results['data']['products'][:5]:
        asin = extract_asin_from_url(product['product_url'])
        asins.append(asin)
    
    # return {'asins': asins}
    return asins[0] if asins else "B09TMN58KL"

async def amazon_product_asins_iter(query: str, page: int, country: str, sort_by: str, product_condition: str) -> dict:
    """
    Asynchronously searches Amazon and returns a list of product ASINs using specified parameters via the RapidAPI service.
    
    Args:
        query (str): The search query string.
        page (int): The page number of search results.
        country (str): The country code for the search.
        sort_by (str): The sorting method for the search results.
        product_condition (str): The condition of the products.

    Returns:
        dict: A dictionary containing a list of product ASINs or an error message.
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

def amazon_product_asins(query: str, page: int = 1, country: str = "US", sort_by: str = "RELEVANCE", product_condition: str = "ALL") -> dict:
    """
    A synchronous wrapper function to search Amazon and return a list of product ASINs.

    Args:
        query (str): The search query string.
        page (int): The page number of search results.
        country (str): The country code for the search.
        sort_by (str): The sorting method for the search results.
        product_condition (str): The condition of the products.

    Returns:
        dict: The result from the asynchronous search function, containing a list of product ASINs or an error message.
    """
    return asyncio.run(amazon_product_asins_iter(query, page, country, sort_by, product_condition))

if __name__ == "__main__":
    search_query = "kindle"  # Replace 'Phone' with your actual search query
    product_asins = amazon_product_asins(search_query, page=1, country="US", sort_by="RELEVANCE", product_condition="ALL")
    print("Product ASINs:", product_asins)
