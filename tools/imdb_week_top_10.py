import asyncio
import requests
from pydantic import BaseModel, Field
from datetime import datetime

# Function to convert timestamp to readable date
def convert_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

def process_response(response):
    if response['status']:
        movies = []
        for item in response['data']:
            if item['titleType']['text'] == 'Movie':
                movie_info = {
                    'id': item['id'],
                    'title': item['originalTitleText']['text'],
                    'type': item['titleType']['text'],
                    'rating': item['ratingsSummary']['aggregateRating'],
                    'release_date': f"{item['releaseDate']['year']}-{item['releaseDate']['month']:02d}-{item['releaseDate']['day']:02d}",
                    'current_rank': item['chartMeterRanking']['currentRank']
                }
                movies.append(movie_info)
        return {
            'message': response['message'],
            'timestamp': convert_timestamp(response['timestamp']),
            'movies': movies
        }
    else:
        return {
            'message': 'Failed to retrieve data'
        }

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
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "imdb188.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return process_response(response.json())
        else:
            return {"error": f"Failed to fetch week's top 10, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def fetch_week_top_10() -> dict:
    """
    A synchronous wrapper function to fetch the week's top 10 movies and shows from IMDb.

    Returns:
        dict: The result from the asynchronous fetch function, containing either the week's top 10 or an error message.
    """
    return asyncio.run(fetch_week_top_10_iter())

if __name__ == "__main__":
    week_top_10_data = fetch_week_top_10()
    print("Week's Top 10:", week_top_10_data)
