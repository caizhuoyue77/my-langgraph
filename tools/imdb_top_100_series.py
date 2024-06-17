import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class IMDbTopSeriesInput(BaseModel):
    query: str = Field(description="用于请求IMDb前100部系列的查询字符串。")

async def fetch_imdb_top_100_series_iter() -> dict:
    """
    Asynchronously fetches the top 100 series list from IMDb via the RapidAPI service.
    
    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://imdb-top-100-movies.p.rapidapi.com/series/"
    headers = {
        "X-RapidAPI-Key": api_keys[0],
        "X-RapidAPI-Host": "imdb-top-100-movies.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return process_top_20_series(response.json())
        else:
            return {"error": f"Failed to fetch IMDb top 100 series, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def process_top_20_series(series_data):
    top_20_series = []
    for serie in series_data[:10]:
        serie_info = {
            'rank': serie['rank'],
            'title': serie['title'],
            'description': serie['description'],
            'year': serie['year']
        }
        top_20_series.append(serie_info)
    return top_20_series

def top_100_series(query:str = "") -> dict:
    """
    A synchronous wrapper function to fetch the IMDb top 100 series.

    Returns:
        dict: The result from the asynchronous fetch function, containing either the top 100 series or an error message.
    """
    return asyncio.run(fetch_imdb_top_100_series_iter())

if __name__ == "__main__":
    series_data = top_100_series("")
    print("IMDb Top 100 Series:", series_data)
