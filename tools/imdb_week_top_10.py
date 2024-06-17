import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *
from datetime import datetime


def process_week_top10_data(week_top10_data):
    data = []
    for item in week_top10_data['data']:
        new_item = {}
        new_item['title'] = item['titleText']['text']
        new_item['rating'] = item['ratingsSummary']['aggregateRating']
        new_item['releaseDate'] = item['releaseDate']
        data.append(new_item)
        
    return {"week_top_10":data}

class WeekTop10Input(BaseModel):
    description: str = Field(default="Fetches the top 10 movies and shows for the week.", description="描述这个API请求的功能。")

async def fetch_week_top_10_iter() -> dict:
    """
    Asynchronously fetches the week's top 10 movies and shows from IMDb via the RapidAPI service.
    
    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://imdb188.p.rapidapi.com/api/v1/getWeekTop10"
    headers = {
        "X-RapidAPI-Key": api_keys[0],
        "X-RapidAPI-Host": "imdb188.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return process_week_top10_data(response.json())
        else:
            return {"error": f"Failed to fetch week's top 10, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def week_top_10(query : str = "") -> dict:
    """
    A synchronous wrapper function to fetch the week's top 10 movies and shows from IMDb.

    Returns:
        dict: The result from the asynchronous fetch function, containing either the week's top 10 or an error message.
    """
    return asyncio.run(fetch_week_top_10_iter())

if __name__ == "__main__":
    week_top_10_data = week_top_10()
    print("Week's Top 10:", week_top_10_data)
