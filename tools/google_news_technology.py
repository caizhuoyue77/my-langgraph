import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class GoogleNewsTechnologyInput(BaseModel):
    language: str = Field(default="en-US", description="用于获取Google News科技新闻的语言代码。")
    max_items: int = Field(default=5, description="要返回的最大新闻条目数。")

def process_news_results(news_results, max_items: int):
    processed_items = []
    count = 0
    for item in news_results.get('items', []):
        if count >= max_items:
            break
        processed_item = {
            "title": item["title"],
            "snippet": item["snippet"],
            "publisher": item["publisher"],
            "url": item["newsUrl"]
        }
        processed_items.append(processed_item)
        count += 1

        # Process subnews if exists and space allows
        for sub_item in item.get('subnews', []):
            if count >= max_items:
                break
            processed_sub_item = {
                "title": sub_item["title"],
                "snippet": sub_item["snippet"],
                "publisher": sub_item["publisher"],
                "url": sub_item["newsUrl"]
            }
            processed_items.append(processed_sub_item)
            count += 1

    return {"status": "success", "items": processed_items}

async def google_news_technology_iter(language: str, max_items: int) -> dict:
    """
    Asynchronously retrieves technology news from Google News using specified parameters via the RapidAPI service.
    
    Args:
        language (str): The language code for the news.
        max_items (int): The maximum number of news items to return.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://google-news13.p.rapidapi.com/technology"
    querystring = {"lr": language}
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "google-news13.p.rapidapi.com",
        'Content-Type': "application/json"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_news_results(response.json(), max_items)
        else:
            return {"error": f"Failed to retrieve technology news, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def google_news_technology(language: str = "en-US", max_items: int = 5) -> dict:
    """
    A synchronous wrapper function to retrieve technology news from Google News.

    Args:
        language (str): The language code for the news.
        max_items (int): The maximum number of news items to return.

    Returns:
        dict: The result from the asynchronous news function, containing either the news results or an error message.
    """
    return asyncio.run(google_news_technology_iter(language, max_items))

if __name__ == "__main__":
    news_language = "en-US"  # Replace with your desired language code
    max_items = 5  # Replace with your desired number of items
    google_news_results = google_news_technology(news_language, max_items)
    print("Google News Technology Results:", google_news_results)
