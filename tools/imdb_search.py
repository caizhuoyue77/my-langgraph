import asyncio
import requests
from pydantic import BaseModel, Field

class SearchIMDBInput(BaseModel):
    query: str = Field(description="用于搜索IMDB数据库的查询字符串。")

async def search_imdb_iter(query: str) -> dict:
    """
    Asynchronously searches IMDb using a specified query string via the RapidAPI service.
    
    Args:
        query (str): The search query string.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://imdb188.p.rapidapi.com/api/v1/searchIMDB"
    querystring = {"query": query}
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "imdb188.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to search IMDb, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def search_imdb(query: str) -> dict:
    """
    A synchronous wrapper function to search IMDb.

    Args:
        query (str): The search query string.

    Returns:
        dict: The result from the asynchronous search function, containing either the search results or an error message.
    """
    return asyncio.run(search_imdb_iter(query))

if __name__ == "__main__":
    search_query = "titanic"  # Replace '<REQUIRED>' with your actual search query
    imdb_search_results = search_imdb(search_query)
    print("Search Results:", imdb_search_results)
