import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class GoogleNewsSearchInput(BaseModel):
    keyword: str = Field(description="用于在Google News中搜索的关键字。")
    language: str = Field(default="en-US", description="用于搜索的语言代码。")

def process_news_results(news_results):
    return news_results  # Customize this function based on the expected structure of the news results.

async def google_news_search_iter(keyword: str, language: str) -> dict:
    """
    Asynchronously searches for news on Google News using specified parameters via the RapidAPI service.
    
    Args:
        keyword (str): The keyword for the news search.
        language (str): The language code for the search.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://google-news13.p.rapidapi.com/search"
    querystring = {"keyword": keyword, "lr": language}
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "google-news13.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_news_results(response.json())
        else:
            return {"error": f"Failed to search news, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def google_news_search(keyword: str, language: str = "en-US") -> dict:
    """
    A synchronous wrapper function to search for news on Google News.

    Args:
        keyword (str): The keyword for the news search.
        language (str): The language code for the search.

    Returns:
        dict: The result from the asynchronous news search function, containing either the news results or an error message.
    """
    return asyncio.run(google_news_search_iter(keyword, language))

if __name__ == "__main__":
    search_keyword = "nvidia"  # Replace with your actual search keyword
    news_language = "en-US"  # Replace with your desired language code
    google_news_results = google_news_search(search_keyword, news_language)
    print("Google News Search Results:", google_news_results)
