import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class GoogleNewsSuggestInput(BaseModel):
    keyword: str = Field(description="用于在Google News中建议搜索的关键字。")
    language: str = Field(default="en-US", description="用于建议搜索的语言代码。")

def process_suggest_results(suggest_results):
    return suggest_results['items']  # Customize this function based on the expected structure of the suggest results.

async def google_news_suggest_iter(keyword: str, language: str) -> dict:
    """
    Asynchronously retrieves search suggestions from Google News using specified parameters via the RapidAPI service.
    
    Args:
        keyword (str): The keyword for the search suggestions.
        language (str): The language code for the suggestions.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://google-news13.p.rapidapi.com/search/suggest"
    querystring = {"keyword": keyword, "lr": language}
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "google-news13.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_suggest_results(response.json())
        else:
            return {"error": f"Failed to retrieve search suggestions, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def google_news_suggest(keyword: str, language: str = "en-US") -> dict:
    """
    A synchronous wrapper function to retrieve search suggestions from Google News.

    Args:
        keyword (str): The keyword for the search suggestions.
        language (str): The language code for the suggestions.

    Returns:
        dict: The result from the asynchronous suggest function, containing either the suggest results or an error message.
    """
    return asyncio.run(google_news_suggest_iter(keyword, language))

if __name__ == "__main__":
    search_keyword = "facebook"  # Replace with your actual search keyword
    suggest_language = "en-US"  # Replace with your desired language code
    google_news_suggest_results = google_news_suggest(search_keyword, suggest_language)
    print("Google News Suggest Results:", google_news_suggest_results)
