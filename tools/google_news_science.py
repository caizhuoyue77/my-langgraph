import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class GoogleNewsScienceInput(BaseModel):
    language: str = Field(default="en-US", description="用于获取Google News科学新闻的语言代码。")

def process_news_results(news_results):
    return news_results  # Customize this function based on the expected structure of the news results.

async def google_news_science_iter(language: str) -> dict:
    """
    Asynchronously retrieves science news from Google News using specified parameters via the RapidAPI service.
    
    Args:
        language (str): The language code for the news.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://google-news13.p.rapidapi.com/science"
    querystring = {"lr": language}
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "google-news13.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_news_results(response.json())
        else:
            return {"error": f"Failed to retrieve science news, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def google_news_science(language: str = "en-US") -> dict:
    """
    A synchronous wrapper function to retrieve science news from Google News.

    Args:
        language (str): The language code for the news.

    Returns:
        dict: The result from the asynchronous news function, containing either the news results or an error message.
    """
    return asyncio.run(google_news_science_iter(language))

if __name__ == "__main__":
    news_language = "en-US"  # Replace with your desired language code
    google_news_results = google_news_science(news_language)
    print("Google News Science Results:", google_news_results)
