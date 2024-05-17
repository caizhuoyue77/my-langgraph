import asyncio
import requests
from pydantic import BaseModel, Field

class UpcomingMoviesInput(BaseModel):
    region: str = Field(default="US", description="The region for which to fetch upcoming movies.")

async def fetch_upcoming_movies_iter(region: str) -> dict:
    """
    Asynchronously fetches a list of upcoming movies for a specified region from IMDb via the RapidAPI service.
    
    Args:
        region (str): The region code for which to fetch upcoming movies.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://imdb188.p.rapidapi.com/api/v1/getUpcomingMovies"
    querystring = {"region": region}
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "imdb188.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch upcoming movies for region {region}, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def fetch_upcoming_movies(region: str = "US") -> dict:
    """
    A synchronous wrapper function to fetch a list of upcoming movies for a specified region from IMDb.

    Args:
        region (str): The region code, defaults to 'US'.

    Returns:
        dict: The result from the asynchronous fetch function, containing either the upcoming movies list or an error message.
    """
    return asyncio.run(fetch_upcoming_movies_iter(region))

if __name__ == "__main__":
    upcoming_movies_data = fetch_upcoming_movies()
    print("Upcoming Movies:", upcoming_movies_data)
